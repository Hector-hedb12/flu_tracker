from time import sleep
from datetime import datetime
import pytz

from django.conf import settings
from django.contrib.gis.geos import Point

from tweepy import OAuthHandler, API, RateLimitError, Cursor
from tweepy.error import TweepError


EST = pytz.timezone('America/New_York')


def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except RateLimitError:
            sleep(15 * 60)      # 15 minutes


def tweet_search(polygon):
    border_points = [Point(coords, srid=3857) for coords in polygon.boundary.array[1:]]  # EPSG:3857 (Pseudo-Mercator)

    # get the triangle centroid
    x_points, y_points = zip(*border_points)
    cx = sum(x_points) / len(border_points)
    cy = sum(y_points) / len(border_points)

    centroid = Point(x=cx, y=cy, srid=3857)

    # get radius for query
    max_distance = 0

    for point in border_points:
        d = centroid.distance(point)  # meters
        if d > max_distance:
            max_distance = d

    wgs84_centroid = centroid.transform(4326, clone=True)  # EPSG:4326 (WGS84)
    geocode = '{},{},{}km'.format(wgs84_centroid.y, wgs84_centroid.x, max_distance / 1000)

    auth = OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(settings.TWITTER_ACCESS_TOKEN_KEY, settings.TWITTER_ACCESS_TOKEN_SECRET)

    api = API(auth)

    cursor = Cursor(
        api.search,
        q=settings.TWITTER_QUERY,
        lang=settings.TWITTER_QUERY_LANGUAGE,
        rpp=settings.TWITTER_QUERY_TWEETS_PER_PAGE,
        geocode=geocode,
    )

    try:
        for status in cursor.items():
            print(status.text)
    except TweepError:
        status = api.rate_limit_status()['resources']['search']
        next_time = datetime.fromtimestamp(status['/search/tweets']['reset']).replace(tzinfo=EST)

        print('#### TweepError ####')
        print('Try again at {}'.format(next_time))

    return []
