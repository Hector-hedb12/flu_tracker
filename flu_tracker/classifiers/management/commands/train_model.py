from pandas import read_csv
from os import makedirs

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Train the specified model'

    def add_arguments(self, parser):
        parser.add_argument(
            '-m',
            '--model',
            dest='model',
            help='model to train'
        )

    def handle(self, *args, **options):
        makedirs(str(settings.MODEL_DIR), exist_ok=True)

        df = read_csv(
            str(settings.DATASET_DIR.path('AwarenessVsInfection2012TweetIDs.csv'))
        )

        classifier_pipeline = Pipeline([
            ('vectorizer', CountVectorizer()),       # text --> matrix of token counts
            ('term_frequency', TfidfTransformer()),  # count matrix -->  normalized TF or TF-IDF
            ('classifier', MultinomialNB())          # Naive Bayes (NB)
        ])

        scores = cross_val_score(classifier_pipeline, df.text, df.target, cv=5)
        accuracy = 'accuracy: %0.2f (+/- %0.2f)' % (scores.mean(), scores.std() * 2)
        self.stdout.write('* {}: {}'.format('Naive Bayes', accuracy))

        classifier_pipeline = Pipeline([
            ('vectorizer', CountVectorizer()),       # text --> matrix of token counts
            ('term_frequency', TfidfTransformer()),  # count matrix -->  normalized TF or TF-IDF
            ('svm', SGDClassifier(                   # Support Vector Machine
                loss='hinge', penalty='l2', alpha=1e-3,
                max_iter=5, random_state=42
            ))
        ])

        scores = cross_val_score(classifier_pipeline, df.text, df.target, cv=5)
        accuracy = 'accuracy: %0.2f (+/- %0.2f)' % (scores.mean(), scores.std() * 2)
        self.stdout.write('* {}: {}'.format('Support Vector Machine', accuracy))

        self.stdout.write(self.style.SUCCESS('Classifier trained'))
