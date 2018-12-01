# project/server/main/views.py
from decimal import Decimal

from flask import render_template, Blueprint, request
from flask_babel import gettext
from flask_login import current_user
from flask_api import status

from project.server import db
from project.server.main.serializers import CartSchema
from project.server.models import Product, Cart, CartItem

main_blueprint = Blueprint('main', __name__, )


@main_blueprint.route('/')
def home():
    data = {
        'products': Product.query.all(),
    }
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user=current_user).first()
        data['cart'] = cart
    return render_template('main/home.html', **data)


@main_blueprint.route("/add_to_cart", methods=['POST'])
def add_to_cart():
    """
    List or create notes.
    """
    result = {}
    product_id = request.data.get('id', -1)
    product = Product.query.get(product_id)
    if not product:
        return {'id': gettext('This field is required.')}, status.HTTP_400_BAD_REQUEST
    cart = Cart.query.filter_by(user=current_user).first()
    if not cart:
        cart = Cart(user=current_user)
    ci = CartItem.query.filter_by(product=product, cart=cart).first()
    if not ci:
        ci = CartItem(product=product, cart=cart, quantity=0, price=product.price)
    ci.quantity += 1
    cart.total = 0
    for item in cart.cart_items:
        product = item.product
        qty = item.quantity
        if product.bogof:
            # Subtract even products from qty for "buy one get one free" products
            qty = qty - qty // 2
        item.price = qty * product.price
        cart.total += item.price
    if cart.total > Decimal('20'):
        cart.total *= Decimal('0.9')  # -10% if total is bigger than 20
    if current_user.loyalty_card:
        cart.total *= Decimal('0.98')  # -2% discount for loyalty cards users
    db.session.add(ci)
    db.session.commit()
    result['data'] = CartSchema().dump(cart).data
    return result, status.HTTP_201_CREATED
