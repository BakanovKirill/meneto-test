# project/server/tests/test_main.py
import json
import unittest
from sqlalchemy.sql import func

from flask import url_for

from project.server.models import Product, Cart, CartItem
from project.tests.base import BaseTestCase


class TestApiBlueprint(BaseTestCase):
    def setUp(self):
        super().setUp()
        # self.headers = {'Content-Type': 'application/json', 'Authorization': 'Token %s' % self.user.get_token()}
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Token %s' % self.user.get_token()
        self.client.environ_base['CONTENT_TYPE'] = 'application/json'

    def add_product_to_cart(self, product):
        return self.client.post(
            url_for('api.add_to_cart'),
            json={'product': product.id},
        )

    def test_forbidden(self):
        self.client.environ_base['HTTP_AUTHORIZATION'] = None
        res = self.client.get(
            url_for('api.get_cart'),
        )
        self.assertEqual(res.status_code, 403)

    def test_add_to_cart(self):
        # Ensure 400 error is handled with non-existing product id
        res = self.client.post(
            url_for('api.add_to_cart'),
            json={'product': 123},
        )
        json = res.json
        self.assertEqual(res.status_code, 400)
        self.assertIsNone(Cart.query.first())
        self.assertEqual(json, {'product': 'Please specify a valid product id'})
        # Test adding product
        product = Product.query.first()
        res = self.add_product_to_cart(product)
        data = res.json['data']
        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(Cart.query.first())
        self.assertIsNotNone(data['id'])
        self.assertIsNotNone(data['quantity'], 1)
        self.assertIsNotNone(data['price'], product.price)
        self.assertEqual(data['product']['id'], product.id)
        self.assertEqual(data['product']['title'], product.title)
        res = self.add_product_to_cart(product)
        data = res.json['data']
        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(data['quantity'], 2)

    def test_get_cart(self):
        # Test 404 handled properly
        res = self.client.get(
            url_for('api.get_cart'),
        )
        json = res.json
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json, {'error': 'Not Found'})
        product = Product.query.first()
        self.add_product_to_cart(product)
        res = self.client.get(
            url_for('api.get_cart'),
        )
        json = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(json['cart_items']), 1)
        self.assertEqual(json['user'], self.user.id)
        self.assertEqual(json['total'], str(product.price))

    def test_remove_cart_item(self):
        for product in Product.query.all():
            self.add_product_to_cart(product)

        cart = Cart.query.first()
        total = self.db.session.query(func.sum(CartItem.price).label('total')).first().total
        self.assertEqual(len(cart.cart_items), 3)
        self.assertEqual(cart.total, total)
        cart_item_for_removal = cart.cart_items[0]
        res = self.client.delete(
            url_for('api.remove_cart_item', pk=cart_item_for_removal.id),
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(cart.cart_items), 2)
        self.assertLess(cart.total, total)
        total = self.db.session.query(func.sum(CartItem.price).label('total')).first().total
        self.assertEqual(cart.total, total)

    def test_update_cart_item(self):
        product = Product.query.first()
        res = self.add_product_to_cart(product)
        self.assertEqual(CartItem.query.count(), 1)
        cart_item_data = res.json['data']
        # Test increment quantity
        cart_item_data['quantity'] += 1
        self.assertEqual(cart_item_data['price'], str(product.price))
        res = self.client.put(
            url_for('api.update_cart_item', pk=cart_item_data['id']),
            data=json.dumps(cart_item_data),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        cart_item_data = res.json
        self.assertEqual(cart_item_data['price'], str(product.price * 2))
        # Test auto removal if quantity = 0
        cart_item_data['quantity'] = 0
        res = self.client.put(
            url_for('api.update_cart_item', pk=cart_item_data['id']),
            data=json.dumps(cart_item_data),
            content_type='application/json'
        )
        data = res.json
        self.assertEqual(data, {})
        self.assertEqual(CartItem.query.count(), 0)


if __name__ == '__main__':
    unittest.main()
