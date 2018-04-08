from time import sleep
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pytz

from django.conf import settings
from django.contrib.gis.geos import Point

from tweepy import AppAuthHandler, API, Cursor
from tweepy import TweepError

from flu_tracker.classifiers.utils import load_classifiers
from .models import Tweet, AddressLocator


EST = pytz.timezone('America/New_York')
geolocator = Nominatim()
ADDRESS_DICT = {}


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
    profile_address = status.author.location.upper().strip()

    if profile_address in ADDRESS_DICT:
        return ADDRESS_DICT[profile_address]

    address, created = AddressLocator.objects.get_or_create(address=profile_address)

    if not created:
        ADDRESS_DICT[profile_address] = address.location
        return address.location

    try:
        location = geolocator.geocode(profile_address)
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None

    if location:
        pnt = Point(x=location.longitude, y=location.latitude, srid=4326).transform(3857, clone=True)
        address.location = pnt
        address.save()

        ADDRESS_DICT[profile_address] = pnt
        return pnt

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

    models = load_classifiers()

    # process query
    result = [centroid]
    tweets = []

    # load addresses to memory
    for addr in AddressLocator.objects.all():
        ADDRESS_DICT[addr.address] = addr.location

    for query in settings.TWITTER_QUERIES:
        cursor = Cursor(
            api.search,
            q=query,
            lang=settings.TWITTER_QUERY_LANGUAGE,
            rpp=settings.TWITTER_QUERY_TWEETS_PER_PAGE,
            geocode=geocode,
        )

        try:
            for status in cursor.items(settings.TWITTER_QUERY_TWEETS_PER_PAGE):
                text = status.text
                if models['related-notrelated'].predict([text])[0] == 1 and \
                   models['awareness-infection'].predict([text])[0] == 0 and \
                   models['self-others'].predict([text])[0] == 1:
                    point = get_point_from_status(status)
                    if point and polygon.contains(point):
                        tweets.append(Tweet(ref=status.id, location=point))
                        result.append(point)
        except TweepError:
            status = api.rate_limit_status()['resources']['search']
            next_time = datetime.fromtimestamp(status['/search/tweets']['reset'])

            print('Rate limit exceeded. Trying again at ({}) --> {} ...'.format(
                status['/search/tweets']['reset'],
                next_time.replace(tzinfo=pytz.utc).astimezone(EST)
            ))

            waiting_sec = (next_time - datetime.now()).total_seconds() + 5
            sleep(waiting_sec)

            print('Trying again ...')

    Tweet.objects.bulk_create(tweets)
    return result
