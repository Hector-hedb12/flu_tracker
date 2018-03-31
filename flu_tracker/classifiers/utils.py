from pickle import load

from django.conf import settings


def load_classifiers():
    classifiers = {
        'awareness-infection': None,
        'related-notrelated': None,
        'self-others': None,
    }

    for model in classifiers:
        with open(str(settings.MODEL_DIR.path('{}-model.pkl'.format(model))), 'rb') as f:
            classifiers[model] = load(f)

    return classifiers
