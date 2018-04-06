from time import sleep
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pytz

from django.conf import settings
from django.contrib.gis.geos import Point

from tweepy import AppAuthHandler, API, Cursor
from tweepy.error import TweepError

from flu_tracker.classifiers.utils import load_classifiers
from .models import Tweet


EST = pytz.timezone('America/New_York')
geolocator = Nominatim()


def get_point_from_status(status):
    # x: longitude, y: latitude

    if status.geo:
        coordinates = status.geo['coordinates']
        return Point(x=coordinates[1], y=coordinates[0], srid=4326).transform(3857, clone=True)

    if status.coordinates:
        coordinates = status.geo['coordinates']
        return Point(x=coordinates[0], y=coordinates[1], srid=4326).transform(3857, clone=True)

    if status.place:
        coordinates = status.place.bounding_box.coordinates[0][0]
        return Point(x=coordinates[0], y=coordinates[1], srid=4326).transform(3857, clone=True)

    # get coordinates from user's profile
    try:
        location = geolocator.geocode(status.author.location)
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None

    if location:
        return Point(x=location.longitude, y=location.latitude, srid=4326).transform(3857, clone=True)

    return None


def tweet_search(polygon):
    border_points = [
        Point(x=coords[0], y=coords[1], srid=3857)  # EPSG:3857 (Pseudo-Mercator)
        for coords in polygon.boundary.array[1:]
    ]

    # get the polygon centroid
    polygon_centroid = polygon.centroid
    centroid = Point(x=polygon_centroid.x, y=polygon_centroid.y, srid=3857)

    # get radius for query
    max_distance = 0

    for point in border_points:
        d = centroid.distance(point)  # meters
        if d > max_distance:
            max_distance = d

    wgs84_centroid = centroid.transform(4326, clone=True)  # EPSG:4326 (WGS84)
    geocode = '{},{},{}km'.format(wgs84_centroid.y, wgs84_centroid.x, max_distance / 1000)

    # perform query
    auth = AppAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    api = API(auth)

    cursor = Cursor(
        api.search,
        q=settings.TWITTER_QUERY,
        lang=settings.TWITTER_QUERY_LANGUAGE,
        rpp=settings.TWITTER_QUERY_TWEETS_PER_PAGE,
        geocode=geocode,
    )

    models = load_classifiers()

    # process query
    result = [centroid]
    try:
        for status in cursor.items(settings.TWITTER_QUERY_TWEETS_PER_PAGE):
            text = status.text
            if models['related-notrelated'].predict([text])[0] == 1 and \
               models['awareness-infection'].predict([text])[0] == 0 and \
               models['self-others'].predict([text])[0] == 1:
                point = get_point_from_status(status)
                if point and polygon.contains(point):
                    Tweet.objects.create(ref=status.id, location=point)
                    result.append(point)

    except TweepError:
        status = api.rate_limit_status()['resources']['search']
        next_time = datetime.fromtimestamp(status['/search/tweets']['reset']).replace(tzinfo=EST)

        print('#### TweepError ####')
        print('Try again at {}'.format(next_time))

        sleep(15 * 60)      # 15 minutes

    return result
