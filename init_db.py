from app import create_app, db
from app.models.product import Product
from app.models.sales import Sale

app = create_app()

with app.app_context():
    # Create all database tables
    db.create_all()
    
    # Add some sample data
    sample_product = Product(
        name='Test Product',
        description='Sample product description',
        current_stock=100,
        minimum_stock=10,
        unit_price=19.99
    )
    
    db.session.add(sample_product)
    db.session.commit()
    
    print("Database initialized successfully!")
