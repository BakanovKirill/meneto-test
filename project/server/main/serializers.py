from marshmallow import fields

from project.server import ma
from project.server.models import Cart, CartItem, Product


class PriceMixin():
    price = fields.Decimal(as_string=True)


class ProductSchema(ma.ModelSchema, PriceMixin):
    class Meta:
        model = Product


class CartItemSchema(ma.ModelSchema, PriceMixin):
    product = fields.Nested(ProductSchema, exclude=('cartitem',))

    class Meta:
        model = CartItem


class CartSchema(ma.ModelSchema):
    cart_items = fields.Nested(CartItemSchema, many=True, exclude=('cart',))
    total = fields.Decimal(as_string=True)

    class Meta:
        model = Cart
