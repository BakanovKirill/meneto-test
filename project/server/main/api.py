from flask import g, request, Blueprint
from flask_api import status
from flask_babel import gettext
from flask_httpauth import HTTPTokenAuth
from flask_login import current_user

from project.server import db
from project.server.main.serializers import CartSchema, CartItemSchema
from project.server.main.utils import error_response, validation_error, update_cart
from project.server.models import User, Cart, Product, CartItem
from project.server.user import admin_user_token

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api_blueprint.config = {}

auth = HTTPTokenAuth('Token')


@api_blueprint.record
def record_params(setup_state):
    """Make app config available in blueprint"""
    app = setup_state.app
    api_blueprint.config = dict([(key, value) for (key, value) in app.config.items()])


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


@api_blueprint.route("/cart", methods=['GET'])
@auth.login_required
def get_cart():
    """
    Get serialized Cart data with nested relations.
    Only current user cart is available.
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


@api_blueprint.route("/cart_item/<int:pk>/", methods=['PUT', 'PATCH'])
@auth.login_required
def update_cart_item(pk):
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
    :param pk: CartItem.id
    :return: CartItem json
    """

    ci = CartItem.query.get(pk)
    data = request.data
    partial = True
    if request.method == 'PUT':
        partial = False
    schema = CartItemSchema().load(data, instance=ci, partial=partial)
    cart_item = schema.data
    cart = update_cart(cart_item.cart, cart_item)
    if cart_item.quantity > 0:
        db.session.add(cart_item)
        data = CartItemSchema().dump(cart_item).data
    else:
        db.session.delete(cart_item)
        db.session.add(cart)
        data = {}
    db.session.commit()
    return data, status.HTTP_200_OK


@api_blueprint.route("/cart_item/<int:pk>/", methods=['DELETE'])
@auth.login_required
def remove_cart_item(pk):
    """
    Delete CartItem by id.
    Example:
    DELETE /api/cart_item/1/

    :param pk: CartItem.id
    :return
    """
    result = {'status': 'ok'}
    ci = CartItem.query.get(pk)
    cart = ci.cart
    db.session.delete(ci)
    db.session.commit()
    cart = update_cart(cart)
    db.session.add(cart)
    db.session.commit()
    return result, status.HTTP_200_OK


@api_blueprint.route("/user/<int:pk>/", methods=['PATCH'])
@auth.login_required
def toggle_loyalty_card(pk):
    """
    Endpoint to test the loyalty cards discount
    :param pk:
    :return:
    """
    result = {'card': None}
    if g.user.id != pk:
        return validation_error('id', gettext('Updating another user is not allowed'))
    user = User.query.get(pk)
    result['card'] = user.loyalty_card = not user.loyalty_card
    if user.cart:
        cart = update_cart(user.cart)
        db.session.add(cart)
    db.session.add(user)
    db.session.commit()
    return result, status.HTTP_200_OK
