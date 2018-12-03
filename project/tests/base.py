# project/server/tests/base.py


from flask_testing import TestCase

from project.server import db, create_app
from project.server.models import User, Product

app = create_app()


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('project.server.config.TestingConfig')
        return app

    def setUp(self):
        self.db = db
        db.create_all()
        user = User(email="ad@min.com", password="admin_user")
        db.session.add(user)
        db.session.add(Product(title="Apple", price=2))
        db.session.add(Product(title="Cat", price=10, bogof=True))
        db.session.add(Product(title="Butter", price=4))
        db.session.commit()
        self.user = user

    def tearDown(self):
        db.session.remove()
        db.drop_all()
