# manage.py


import unittest

import click
import coverage

from flask.cli import FlaskGroup

from project.server import create_app, db
from project.server.models import *
import subprocess
import sys

app = create_app()
cli = FlaskGroup(create_app=create_app)
# code coverage
COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/server/config.py',
        'project/server/*/__init__.py'
    ]
)
COV.start()


@cli.command()
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@cli.command()
def create_admin():
    """Creates the admin user."""
    db.session.add(User(email='ad@min.com', password='admin', admin=True))
    db.session.commit()


@cli.command()
def create_data():
    """Creates sample data."""
    db.session.add(Product(title="Cap", price=25, bogof=True))
    db.session.add(Product(title="Banana", price=5))
    db.session.add(Product(title="Apple", price=2))
    db.session.add(Product(title="Cat", price=10, bogof=True))
    db.session.add(Product(title="Butter", price=4))
    db.session.commit()

@cli.command()
@click.option('--test_name')
def test(test_name=None):
    """
    Runs the unit tests without test coverage:

    $ python manage.py test

    test_name usage below to run single test:

    $ python manage.py test  --test_name=test_api.TestApiBlueprint.test_add_to_cart

    """
    if not test_name:
        tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    else:
        tests = unittest.TestLoader().loadTestsFromName('project.tests.%s' % test_name)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def cov():
    """
    Runs the unit tests with coverage:

    $ python manage.py cov

    """
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def flake():
    """Runs flake8 on the project."""
    subprocess.run(['flake8', 'project'])


if __name__ == '__main__':
    cli()
