from flask import Blueprint, jsonify, request
from app.models.product import Product
from app import db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'current_stock': p.current_stock
    } for p in products])
