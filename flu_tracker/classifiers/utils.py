from os import makedirs

import matplotlib.pyplot as plt
import numpy as np

from django.conf import settings

from pickle import load
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_curve
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


def plot_precision_recall_curve(estimator, title, X, y):
    """
    Generate a simple precision recall plot.
    """

    fig = plt.figure()

    if hasattr(estimator, 'decision_function'):
        y_score = estimator.decision_function(X)
    else:
        y_score = estimator.predict_proba(X)[:, 0]

    average_precision = average_precision_score(y, y_score)
    precision, recall, _ = precision_recall_curve(y, y_score)

    plt.step(recall, precision, color='b', alpha=0.2, where='post')
    plt.fill_between(recall, precision, step='post', alpha=0.2, color='b')

    plt.title('{0}: average={1:0.2f}'.format(title, average_precision))

    plt.xlabel('Recall')
    plt.ylabel('Precision')

    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.05])

    # save figure
    directory = str(settings.MODEL_DIR.path('precision_recall_curves'))
    makedirs(directory, exist_ok=True)

    fig.savefig('{}/{}'.format(directory, title))
    plt.close(fig)


def plot_roc_curves(estimators, title, X, y):
    """
    Generate a ROC curves.
    """

    fig = plt.figure()

    plt.plot([0, 1], [0, 1], 'k--')

    for estimator, name in estimators:
        if hasattr(estimator, 'decision_function'):
            y_score = estimator.decision_function(X)
        else:
            y_score = estimator.predict_proba(X)[:, 1]

        fpr, tpr, _ = roc_curve(y, y_score)

        plt.plot(fpr, tpr, label=name)

    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC curve')
    plt.legend(loc='best')

    # save figure
    directory = str(settings.MODEL_DIR.path('roc_curves'))
    makedirs(directory, exist_ok=True)

    fig.savefig('{}/{}'.format(directory, title))
    plt.close(fig)
