from decimal import Decimal

from flask import jsonify
from werkzeug.exceptions import BadRequest
from werkzeug.http import HTTP_STATUS_CODES

from project.server.models import CartItem


def update_cart(cart, cart_item=None):
    cart = cart_item.cart if cart_item else cart
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
    if cart.user.loyalty_card:
        cart.total *= Decimal('0.98')  # -2% discount for loyalty cards users
    return cart


def validation_error(key, message):
    error = BadRequest(message)
    error.data = {key: message}
    raise error


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response
