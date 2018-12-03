# project/server/main/views.py

from flask import render_template, request, g, Blueprint

from project.server.models import Product

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def home():
    data = {
        'products': Product.query.all()
    }
    return render_template('main/home.html', **data)
