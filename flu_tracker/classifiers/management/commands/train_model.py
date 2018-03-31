from pandas import read_csv
from os import makedirs
from numpy import mean

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from django.conf import settings
from django.core.management.base import BaseCommand


CLASS_NAMES = {
    MultinomialNB: 'Naive-Bayes',
    SGDClassifier: 'Support-Vector-Machine',
}


MODEL_CLASSES = {
    'awareness-infection': MultinomialNB,
    'related-notrelated': MultinomialNB,
    'self-others': SGDClassifier,
}

MODEL_PARAMETERS = {
    'awareness-infection': {    # MultinomialNB
        'vectorizer': {
            'ngram_range': (1, 3)
        },
        'term_frequency': {
            'sublinear_tf': True,
            'use_idf': False
        },
        'classifier': {
            'alpha': 0.1
        }
    },
    'related-notrelated': {     # MultinomialNB
        'vectorizer': {},
        'term_frequency': {
            'sublinear_tf': True,
            'use_idf': False,
            'norm': 'l1',
        },
        'classifier': {
            'alpha': 0.1,
            'fit_prior': False,
        }
    },
    'self-others': {            # SGDClassifier
        'vectorizer': {
            'ngram_range': (1, 3)
        },
        'term_frequency': {
            'norm': 'l1'
        },
        'classifier': {
            'alpha': 1e-05,
            'penalty': 'none',
            'warm_start': True
        }
    },
}


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

        for model in MODEL_CLASSES:
            self.stdout.write('')
            self.stdout.write(model)
            self.stdout.write('===================')
            self.stdout.write('')

            df_train = read_csv(str(settings.DATASET_DIR.path(model).path('train.csv')))
            df_test = read_csv(str(settings.DATASET_DIR.path(model).path('test.csv')))

            classifier_pipeline = Pipeline([             # text --> matrix of token counts
                ('vectorizer', CountVectorizer(
                    **MODEL_PARAMETERS[model]['vectorizer']
                )),
                ('term_frequency', TfidfTransformer(     # count matrix -->  normalized TF or TF-IDF
                    **MODEL_PARAMETERS[model]['term_frequency']
                )),
                ('classifier', MODEL_CLASSES[model](     # Naive Bayes (NB) or Support Vector Machine
                    **MODEL_PARAMETERS[model]['classifier']
                ))
            ])

            classifier = classifier_pipeline.fit(df_train.text, df_train.target)
            predicted = classifier.predict(df_test.text)
            accuracy = mean(predicted == df_test.target)

            self.stdout.write('* {}: {}'.format(CLASS_NAMES[MODEL_CLASSES[model]], accuracy))

        self.stdout.write(self.style.SUCCESS('Classifiers trained'))
