from app import db
from app.models import Product

def populate_database():
    products = [
        {
            'name': 'Laptop Dell XPS 13',
            'description': 'High-performance laptop with 16GB RAM, 512GB SSD',
            'current_stock': 15,
            'minimum_stock': 5,
            'unit_price': 1299.99
        },
        {
            'name': 'iPhone 14 Pro',
            'description': '256GB, Graphite, 5G Enabled',
            'current_stock': 25,
            'minimum_stock': 8,
            'unit_price': 999.99
        },
        {
            'name': 'Samsung 4K TV',
            'description': '65-inch QLED Smart TV',
            'current_stock': 10,
            'minimum_stock': 3,
            'unit_price': 1499.99
        },
        {
            'name': 'Sony PS5',
            'description': 'Gaming Console with 825GB SSD',
            'current_stock': 20,
            'minimum_stock': 5,
            'unit_price': 499.99
        }
    ]
    
    for product_data in products:
        new_product = Product(**product_data)
        db.session.add(new_product)
    
    db.session.commit()
