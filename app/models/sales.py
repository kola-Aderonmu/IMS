from app import db
from datetime import datetime

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Product
    product = db.relationship('Product', backref='sales')

    def __repr__(self):
        return f'<Sale {self.id} of Product {self.product_id}>'
