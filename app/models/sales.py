from app import db
from datetime import datetime

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(100))
    sale_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    #Relationship with product
    product = db.relationship('Product', backref=db.backref('sales', lazy=True))

    def __repr__(self):
        return f'<Sale {self.id} of Product {self.product_id}>'

class SalesAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    total_sales = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    last_sale_date = db.Column(db.DateTime)
    average_sale_price = db.Column(db.Float, default=0.0)
