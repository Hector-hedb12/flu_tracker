from datetime import datetime
from pandas import DataFrame
from os import makedirs
from os.path import basename, splitext
from time import sleep
from tqdm import tqdm

import pytz

from tweepy import OAuthHandler, API
from tweepy import TweepError, RateLimitError

from django.conf import settings
from django.core.management.base import BaseCommand


EST = pytz.timezone('America/New_York')


def get_tweets(ids):
    error_getting_tweet = False

    auth = OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(settings.TWITTER_ACCESS_TOKEN_KEY, settings.TWITTER_ACCESS_TOKEN_SECRET)

    api = API(auth)

    tweets = {}

    ids = tqdm(ids, desc='Getting tweets')

    for id in ids:
        while True:
            try:
                tweet = api.get_status(id)
            except RateLimitError:
                status = api.rate_limit_status()['resources']['statuses']
                next_time = datetime.fromtimestamp(status['/statuses/show/:id']['reset'])

                print('Rate limit exceeded. Trying again at ({}) --> {} ...'.format(
                    status['/statuses/show/:id']['reset'],
                    next_time.replace(tzinfo=pytz.utc).astimezone(EST)
                ))

                waiting_sec = (next_time - datetime.now()).total_seconds() + 5
                sleep(waiting_sec)

                print('Trying id={} again ...'.format(id))

                continue

            except TweepError:
                error_getting_tweet = True
            else:
                tweets[id] = tweet.text.replace('\n', ' ')
            break

    if error_getting_tweet:
        print('It was not possible to retrieve {} tweets ...'.format(len(ids) - len(tweets.keys())))

    return tweets


class Command(BaseCommand):
    help = 'Download the specified tweets'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='file',
            help='file to read ids from tweets'
        )

    def handle(self, *args, **options):
        makedirs(str(settings.DATASET_DIR), exist_ok=True)

        fname = splitext(basename(options['file']))[0] + '.csv'
        data = {}

        # retrieve data
        with open(options['file'], 'r') as f:
            for line in f:
                id, label = line.split('\t')
                data[id] = int(label[0])

        result = get_tweets(data.keys())

        # save data
        texts = []
        labels = []

        for id in result:
            texts.append(result[id])
            labels.append(data[id])

        df = DataFrame({'text': texts, 'target': labels})
        df.to_csv(str(settings.DATASET_DIR.path(fname)), index=False)

        self.stdout.write(self.style.SUCCESS(
            'Read {} tweets from file {}'.format(len(result), options['file'])
        ))
