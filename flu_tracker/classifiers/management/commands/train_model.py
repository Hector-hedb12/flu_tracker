from pandas import read_csv
from os import makedirs
from numpy import mean

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
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

        model = 'awareness-infection'
        df_train = read_csv(str(settings.DATASET_DIR.path(model).path('train.csv')))
        df_test = read_csv(str(settings.DATASET_DIR.path(model).path('test.csv')))

        # 1.
        classifier_pipeline = Pipeline([
            ('vectorizer', CountVectorizer()),       # text --> matrix of token counts
            ('term_frequency', TfidfTransformer()),  # count matrix -->  normalized TF or TF-IDF
            ('classifier', MultinomialNB())          # Naive Bayes (NB)
        ])

        classifier = classifier_pipeline.fit(df_train.text, df_train.target)
        predicted = classifier.predict(df_test.text)
        accuracy = mean(predicted == df_test.target)

        self.stdout.write('* {}: {}'.format('Naive Bayes', accuracy))

        # 2.
        classifier_pipeline = Pipeline([
            ('vectorizer', CountVectorizer()),       # text --> matrix of token counts
            ('term_frequency', TfidfTransformer()),  # count matrix -->  normalized TF or TF-IDF
            ('svm', SGDClassifier(                   # Support Vector Machine
                loss='hinge', penalty='l2', alpha=1e-3,
                max_iter=5, random_state=42
            ))
        ])

        classifier = classifier_pipeline.fit(df_train.text, df_train.target)
        predicted = classifier.predict(df_test.text)
        accuracy = mean(predicted == df_test.target)

        self.stdout.write('* {}: {}'.format('Support Vector Machine', accuracy))

        # end
        self.stdout.write(self.style.SUCCESS('Classifier trained'))
