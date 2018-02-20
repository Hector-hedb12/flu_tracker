=============
 Flu Tracker
=============

The Flu Tracker ...

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django


:License: MIT


Project Layout
--------------

This project follows the three-tired approach specified in
*Two Scoops of Django - Best Practices for Django 2.0*::

     <repository_root>/
        <django_project_root>/
           <configuration_root>/



Pre-Installations
-----------------

1. Install pip::

     $ sudo apt-get install python-pip python-dev build-essential

#. Install virtualenv::

     $ sudo pip install virtualenvwrapper

#. Add to end of file ``~/.bashrc`` this line::

     $ source /usr/local/bin/virtualenvwrapper.sh

#. Install postgresql, libraries and header for C language backend development (change ``X.Y`` to a version number)::

     $ sudo apt-get install postgresql-X.Y postgresql-server-dev-X.Y postgresql-X.Y-postgis-scripts

#. Restart terminal


Project configurations
----------------------

1. Open psql console::

     $ sudo -u postgres psql

#. Create flu_tracker database::

     # create database flu_tracker;

#. Create flu_tracker user::

     # create user flu_tracker with password 'flu_tracker_pass' createdb;

#. Grant all available privileges to user flu_tracker on flu_tracker database::

     # grant all privileges on database flu_tracker to flu_tracker;

#. Create ``postgis`` extension::

     # create extension postgis;

#. Exit psql console::

     # \q


Project Installations
---------------------

1. Go to repostory root directory ``flu_tracker/``
#. Create a virtualenv for the project::

     $ mkvirtualenv flu_tracker

#. Install requeriments::

     $ pip install -r requirements/local.txt

#. Run migrations::

     $ python manage.py migrate

#. Create superuser::

     $ python manage.py createsuperuser


Run Project
-----------

1. Activate enviorment::

     $ workon flu_tracker

#. Open a new terminal, go to the repostory root directory ``flu_tracker/``, at the same level of ``manage.py`` file and execute::

     $ python manage.py runserver

#. That's it ! You can open localhost in a browser, and sign in with the user and password created in Project Installations section.
