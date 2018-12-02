# project/server/models.py


import datetime

from flask import current_app
from sqlalchemy.orm import backref

from project.server import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    loyalty_card = db.Column(db.Boolean, default=False)

    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=True)
    cart = db.relationship('Cart', backref=backref("user", uselist=False), uselist=False, lazy='joined')

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode('utf-8')
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    # Constants
    ADD = 'add'
    SUBTRACT = 'subtract'
    REMOVE = 'remove'
    ACTIONS = (ADD, SUBTRACT, REMOVE)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Numeric(asdecimal=True, precision=10, scale=2), nullable=False)

    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=True)
    cart = db.relationship('Cart', backref=backref("cart_items", lazy='joined', cascade="all, delete-orphan"),
                           lazy=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product = db.relationship('Product', backref="cartitem", uselist=False, lazy='joined')


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(asdecimal=True, precision=10, scale=2), nullable=False)
    bogof = db.Column(db.Boolean, default=False)


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    total = db.Column(db.Numeric(asdecimal=True, precision=10, scale=2), default=0)
