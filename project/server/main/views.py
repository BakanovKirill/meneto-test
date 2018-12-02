# project/server/main/views.py

from flask import render_template, Blueprint, request, g, make_response, jsonify
from flask_babel import gettext
from flask_login import current_user
from flask_api import status
from sqlalchemy.orm import joinedload

from project.server import db
from flask_httpauth import HTTPTokenAuth
from project.server.main.serializers import CartSchema, CartItemSchema
from project.server.main.utils import validation_error, update_cart, error_response
from project.server.models import Product, Cart, CartItem, User
from project.server.user import admin_user_token

main_blueprint = Blueprint('main', __name__)
api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api_blueprint.config = {}

auth = HTTPTokenAuth('Token')


@api_blueprint.app_errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request_handler(resp):
    return resp.data, status.HTTP_400_BAD_REQUEST


@api_blueprint.app_errorhandler(status.HTTP_404_NOT_FOUND)
def not_found_handler(resp):
    return {'message': 'Not found'}, status.HTTP_404_NOT_FOUND


@auth.error_handler
def token_auth_error():
    """
    Replace 401 auth error with 403 to avoid browser auth popup window.
    :return:
    """
    return error_response(status.HTTP_403_FORBIDDEN)


@auth.verify_token
def authenticate(token):
    """
    Combine session auth and token auth by checking token or current_user.

    :param token: value from HTTP Header "Authentication: Token <value>"
    :return: True in case of success, False otherwise which raises 401
    """
    if token == admin_user_token or current_user.is_authenticated:
        # Hardcoded user to avoid extra time investment into storing/generating tokens.
        g.user = User.query.filter_by(email='ad@min.com').first()
        return True
    return False


@api_blueprint.record
def record_params(setup_state):
    """Make app config available in blueprint"""
    app = setup_state.app
    api_blueprint.config = dict([(key, value) for (key, value) in app.config.items()])


@main_blueprint.route('/')
def home():
    data = {
        'products': Product.query.all()
    }
    return render_template('main/home.html', **data)


@api_blueprint.route("/cart", methods=['GET'])
@auth.login_required
def cart():
    """
    Get serialized Cart data with nested relations.
    :return:
    """
    user = g.user
    cart = Cart.query.filter_by(user=user).first()
    if not cart:
        return error_response(status.HTTP_404_NOT_FOUND)
    return CartSchema().dump(cart).data


@api_blueprint.route("/cart_item", methods=['POST'])
@auth.login_required
def add_to_cart():
    """
    Receive a POST with only Product.ID, this is the only required field to remove the calculations from front-end.

    Creates CartItem with given product and Cart if needed.

    Example:

    POST /api/cart_item/
    {
        product: 1
    }
    :return CartItem json
    """
    result = {}
    product_id = request.data.get('product', -1)
    product = Product.query.get(product_id)
    user = g.user

    if not product:
        return validation_error('product', gettext('Please specify a valid product id'))
    cart = Cart.query.filter_by(user=user).first()
    if not cart:
        cart = Cart(user=user)
    cart_item = CartItem.query.filter_by(cart=cart, product=product).first()
    if not cart_item:
        cart_item = CartItem(product=product, cart=cart, quantity=1, price=product.price)
    else:
        cart_item.quantity += 1
    # Increment item quantity, calculate cart.total and cart_item.price
    update_cart(cart, cart_item)
    db.session.add(cart_item)
    db.session.commit()

    result['data'] = CartItemSchema().dump(cart_item).data
    return result, status.HTTP_201_CREATED


@api_blueprint.route("/cart_item/<int:id>/", methods=['PUT', 'PATCH'])
@auth.login_required
def update_cart_item(id):
    """
    Updated specified CartItem. Used to increment/decrement item quantity in Cart.
    Can be partial update.
    Example:
    PUT /api/cart_item/2/
     {
        "product": {
            "price": "5.00",
            "bogof": False,
            "title": "Banana",
            "id": 2
        },
        "quantity": 2,
        "price": "5.00",
        "id": 2
    }
    :param id: CartItem.id
    :return: CartItem json
    """

    result = {}
    ci = CartItem.query.get(id)
    data = request.data
    partial = True
    if request.method == 'PUT':
        partial = False
    schema = CartItemSchema().load(data, instance=ci, partial=partial)
    cart_item = schema.data
    cart = update_cart(cart_item.cart, cart_item)
    if cart_item.quantity > 0:
        db.session.add(cart_item)
    else:
        db.session.delete(cart_item)
        db.session.add(cart)
    db.session.commit()
    return CartItemSchema.dump(cart_item).data, status.HTTP_200_OK


@api_blueprint.route("/cart_item/<int:id>/", methods=['DELETE'])
@auth.login_required
def remove_cart_item(id):
    """
    Delete CartItem by id.
    Example:
    DELETE /api/cart_item/1/

    :param id: CartItem.id
    :return
    """
    result = {'status': 'ok'}
    ci = CartItem.query.get(id)
    cart = ci.cart
    db.session.delete(ci)
    db.session.commit()
    cart = update_cart(cart)
    db.session.add(cart)
    db.session.commit()
    return result, status.HTTP_200_OK


@api_blueprint.route("/user/<int:id>/", methods=['PATCH'])
@auth.login_required
def toggle_loyalty_card(id):
    """
    Endpoint to test the loyalty cards discount
    :param id:
    :return:
    """
    result = {'card': None}
    if g.user.id != id:
        return validation_error('id', gettext('Updating another user is not allowed'))
    user = User.query.get(id)
    result['card'] = user.loyalty_card = not user.loyalty_card
    if user.cart:
        cart = update_cart(user.cart)
        db.session.add(cart)
    db.session.add(user)
    db.session.commit()
    return result, status.HTTP_200_OK
