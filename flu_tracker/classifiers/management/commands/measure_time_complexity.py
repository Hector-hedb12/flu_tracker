from os import makedirs

import matplotlib.pyplot as plt
from numpy import arange
from pandas import read_csv
from timeit import timeit

from django.conf import settings
from django.core.management.base import BaseCommand

from ...utils import load_classifiers


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped


def predict(classifier, texts):
    classifier.predict(texts)


class Command(BaseCommand):
    help = 'Measure time complexity of algorithms'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            dest='file',
            help='file with tweets to classify'
        )

    def handle(self, *args, **options):
        # retrieve data
        with open(options['file'], 'r') as f:
            data = read_csv(f)

        classifiers = load_classifiers()

        figures = {'awareness-infection': '-.', 'related-notrelated': '-', 'self-others': '--'}

        times = {
            'awareness-infection': [],
            'related-notrelated': [],
            'self-others': [],
        }

        ticks = arange(1, data.shape[0], 20)
        # run experiments
        for num_samples in ticks:
            for classifier in times:
                wrapped = wrapper(predict, classifiers[classifier], data.Text[:num_samples])
                seconds = timeit(wrapped, number=1)
                times[classifier].append(seconds)

        fig = plt.figure()
        title = 'Prediction Time Complexity'
        plt.title(title)

        for classifier in times:
            plt.plot(ticks, times[classifier], figures[classifier], label=classifier)

        plt.xlabel('Number of Samples')
        plt.ylabel('Seconds')
        plt.title(title)
        plt.legend(loc='best')

        # save figure
        directory = str(settings.MODEL_DIR.path('times'))
        makedirs(directory, exist_ok=True)

        fig.savefig('{}/{}'.format(directory, title))
        plt.close(fig)

        self.stdout.write(self.style.SUCCESS('Plot saved at {}'.format(directory)))
