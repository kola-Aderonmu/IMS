from datetime import datetime, timedelta
from app.models.product import Product
from app.models.sales import Sale
from sqlalchemy import func

def calculate_daily_sales_rate(product_id, days=30):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    total_sales = Sale.query.filter(
        Sale.product_id == product_id,
        Sale.sale_date.between(start_date, end_date)
    ).with_entities(func.sum(Sale.quantity)).scalar() or 0
    
    daily_rate = total_sales / days
    return daily_rate

def get_replenishment_suggestions():
    products = Product.query.all()
    suggestions = []
    
    for product in products:
        daily_rate = calculate_daily_sales_rate(product.id)
        days_until_minimum = 0
        if daily_rate > 0:
            days_until_minimum = (product.current_stock - product.minimum_stock) / daily_rate
        
        suggested_order = 0
        if days_until_minimum <= 7:  # If stock will reach minimum within 7 days
            suggested_order = int(daily_rate * 30)  # Order 30 days worth of stock
        
        suggestions.append({
            'product': product,
            'daily_rate': daily_rate,
            'days_until_minimum': int(days_until_minimum),
            'suggested_order': suggested_order
        })
    
    return suggestions
