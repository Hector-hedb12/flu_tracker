from os import makedirs

import matplotlib.pyplot as plt
import numpy as np

from django.conf import settings

from pickle import load
from sklearn.model_selection import learning_curve, validation_curve


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


def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=1, train_sizes=np.linspace(.1, 1.0, 5)):
    """
    Generate a simple plot of the test and training learning curve.

    Mostly taken from:
    https://github.com/scikit-learn/scikit-learn/blob/0.19.1/examples/model_selection/plot_learning_curve.py
    """

    fig = plt.figure()
    plt.title(title)

    if ylim is not None:
        plt.ylim(*ylim)

    plt.xlabel('Training examples')
    plt.ylabel('Score')

    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes
    )

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color='r')

    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1,
                     color='g')

    plt.plot(train_sizes, train_scores_mean, 'o--', color='r',
             label='Training score')

    plt.plot(train_sizes, test_scores_mean, 'o-', color='g',
             label='Cross-validation score')

    plt.legend(loc='best')

    # save figure
    directory = str(settings.MODEL_DIR.path('learning_curves'))
    makedirs(directory, exist_ok=True)

    fig.savefig('{}/{}'.format(directory, title))
    plt.close(fig)


def plot_validation_curve(estimator, title, X, y, param_name, param_range,
                          ylim=None, cv=None, n_jobs=1):
    """
    Generate a simple plot of the test and training scores for a varying parameter.
    """

    fig = plt.figure()
    plt.title(title)

    if ylim is not None:
        plt.ylim(*ylim)

    plt.xlabel(param_name)
    plt.ylabel('Score')

    train_scores, test_scores = validation_curve(
        estimator, X, y, param_name, param_range, cv=cv, n_jobs=n_jobs
    )

    train_scores_mean = np.mean(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)

    plt.grid()

    plt.plot(param_range, train_scores_mean, 'o--', color='r',
             label='Training score')

    plt.plot(param_range, test_scores_mean, 'o-', color='g',
             label='Cross-validation score')

    plt.legend(loc='best')

    # save figure
    directory = str(settings.MODEL_DIR.path('validation_curves'))
    makedirs(directory, exist_ok=True)

    fig.savefig('{}/{}'.format(directory, title))
    plt.close(fig)
