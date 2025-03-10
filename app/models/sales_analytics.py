from app import db

class SalesAnalytics(db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    total_sales = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    last_sale_date = db.Column(db.DateTime)
    average_sale_price = db.Column(db.Float, default=0.0)
