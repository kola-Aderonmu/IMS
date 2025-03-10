from flask import Blueprint, send_file, request, render_template, redirect, url_for, flash
from app.models.product import Product
from app.services.replenishment import get_replenishment_suggestions
from app.forms import ProductForm, SaleForm
from app.models.sales import Sale
from app.forms import SaleForm
from app.models import product
from flask import send_file
from sqlalchemy import func
from app.services.monitoring import StockMonitor
from app.services.forecasting import SalesForecaster
from app.services.reporting import ReportGenerator
from app import db
from datetime import datetime, timedelta
import json
import io
import plotly
import plotly.express as px
import pandas as pd
import numpy as np
from app.models import Product, sales
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter



bp = Blueprint('main', __name__)


@bp.route('/dashboard')
def dashboard():
    # Calculate total sales for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_sales = db.session.query(func.sum(Sale.quantity)).filter(
        Sale.sale_date >= thirty_days_ago
    ).scalar() or 0

    # New statistics
    best_selling_products = db.session.query(
        Product.name,
        func.sum(Sale.quantity).label('total_sold')
    ).join(Sale).group_by(Product.id).order_by(
        func.sum(Sale.quantity).desc()
    ).limit(5).all()

    out_of_stock = Product.query.filter(Product.current_stock == 0).count()

    total_inventory_value = db.session.query(
        func.sum(Product.current_stock * Product.unit_price)
    ).scalar() or 0

    recent_sales = db.session.query(
        Sale, Product
    ).join(Product).order_by(
        Sale.sale_date.desc()
    ).limit(5).all()

    # Get all products
    products = Product.query.all()

    # Get low stock products
    low_stock_products = Product.query.filter(
        Product.current_stock <= Product.minimum_stock
    ).all()

    # Calculate total revenue
    total_revenue = db.session.query(
        func.sum(Sale.quantity * Product.unit_price)
    ).join(Product).scalar() or 0

    # Get sales trend data
    sales_trend = db.session.query(
        func.date(Sale.sale_date),
        func.sum(Sale.quantity)
    ).group_by(
        func.date(Sale.sale_date)
    ).order_by(
        func.date(Sale.sale_date)
    ).all()

    # Chart data preparation
    sales_data = {
        'labels': [sale[0].strftime('%Y-%m-%d') for sale in sales_trend],
        'values': [sale[1] for sale in sales_trend]
    }
    
    stock_data = {
        'labels': [p.name for p in products],
        'values': [p.current_stock for p in products]
    }
    
    revenue_data = {
        'labels': [sale[0].strftime('%Y-%m-%d') for sale in sales_trend],
        'values': [sale[1] * products[0].unit_price for sale in sales_trend]
    }
    
    top_products = {
        'labels': [product[0] for product in best_selling_products],
        'values': [product[1] for product in best_selling_products]
    }

    return render_template('dashboard.html',
        total_sales=total_sales,
        products=products,
        low_stock_products=low_stock_products,
        total_revenue=total_revenue,
        best_selling_products=best_selling_products,
        out_of_stock=out_of_stock,
        total_inventory_value=total_inventory_value,
        recent_sales=recent_sales,
        sales_data=sales_data,
        stock_data=stock_data,
        revenue_data=revenue_data,
        top_products=top_products
    )


def create_sales_graph(sales_data):
    import plotly.express as px
    import pandas as pd
    
    df = pd.DataFrame(sales_data, columns=['date', 'quantity'])
    fig = px.line(df, x='date', y='quantity', title='Daily Sales Trend')
    return fig.to_json()



@bp.route('/')
def index():
    products = Product.query.all()
    return redirect(url_for('main.dashboard'))

@bp.route('/product/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            current_stock=form.current_stock.data,
            minimum_stock=form.minimum_stock.data,
            unit_price=form.unit_price.data
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{product.name}" has been successfully added!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_product.html', form=form)



# @bp.route('/record_sale', methods=['GET', 'POST'])
# def record_sale():
#     form = SaleForm()
#     products = Product.query.all()
    
#     # Fix the price attribute by using unit_price instead
#     form.product_id.choices = [(p.id, f"{p.name} - ${p.unit_price}") for p in products]
    
#     if form.validate_on_submit():
#         product = Product.query.get(form.product_id.data)
#         if product.current_stock >= form.quantity.data:
#             sale = Sale(
#                 product_id=form.product_id.data,
#                 quantity=form.quantity.data,
#                 unit_price=product.unit_price,
#                 total_amount=product.unit_price * form.quantity.data
#             )
            
#             product.current_stock -= form.quantity.data
#             db.session.add(sale)
#             db.session.commit()
            
#             flash('Sale recorded successfully!', 'success')
#             return redirect(url_for('main.record_sale'))
#         else:
#             flash(f'Not enough stock available! Current stock: {product.current_stock}', 'error')
    
#     return render_template('record_sale.html', form=form)


@bp.route('/record_sale', methods=['GET', 'POST'])
def record_sale():
    form = SaleForm()
    products = Product.query.all()
    form.product_id.choices = [(p.id, f"{p.name} - ${p.unit_price}") for p in products]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if product.current_stock >= form.quantity.data:
            sale = Sale(
                product_id=form.product_id.data,
                quantity=form.quantity.data,
                unit_price=product.unit_price,
                total_amount=product.unit_price * form.quantity.data
            )
            
            product.current_stock -= form.quantity.data
            update_sales_analytics(product, sale)  # Correct indentation
            db.session.add(sale)
            db.session.commit()
            
            flash('Sale recorded successfully!', 'success')
            return redirect(url_for('main.record_sale'))
        
        flash(f'Not enough stock available! Current stock: {product.current_stock}', 'error')
    
    return render_template('record_sale.html', form=form)

            
            # Update analytics
    update_sales_analytics(product, sale)
            
            # Generate invoice
    invoice_pdf = generate_invoice(sale, product)
            
    db.session.commit()
    flash('Sale recorded successfully!', 'success')
            
            # Return invoice
    return send_file(
                io.BytesIO(invoice_pdf),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'invoice_{sale.id}.pdf'
            )
            
    flash(f'Not enough stock available! Current stock: {product.current_stock}', 'error')
    
    return render_template('record_sale.html', form=form)

def update_sales_analytics(product, sale):
    """Update sales analytics data"""
    analytics = SalesAnalytics.query.filter_by(product_id=product.id).first()
    if not analytics:
        analytics = SalesAnalytics(product_id=product.id)
        db.session.add(analytics)
    
    analytics.total_sales += sale.quantity
    analytics.total_revenue += sale.total_amount
    analytics.last_sale_date = datetime.now()
    analytics.average_sale_price = (analytics.total_revenue / analytics.total_sales)

def generate_invoice(sale, product):
    """Generate PDF invoice"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add invoice header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "SALES INVOICE")
    
    # Add sale details
    p.setFont("Helvetica", 12)
    p.drawString(50, 700, f"Invoice #: {sale.id}")
    p.drawString(50, 680, f"Date: {sale.sale_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Add product details
    p.drawString(50, 630, f"Product: {product.name}")
    p.drawString(50, 610, f"Quantity: {sale.quantity}")
    p.drawString(50, 590, f"Unit Price: ${sale.unit_price:.2f}")
    p.drawString(50, 570, f"Total Amount: ${sale.total_amount:.2f}")
    
    p.save()
    return buffer.getvalue()



@bp.route('/product/<int:product_id>/add-stock', methods=['GET', 'POST'])
def add_stock(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 0))
        if quantity > 0:
            product.current_stock += quantity
            db.session.commit()
            flash(f'Added {quantity} units to {product.name}', 'success')
            return redirect(url_for('main.product_list'))
    
    return render_template('add_stock.html', product=product)




@bp.route('/replenishment')
def replenishment():
    suggestions = get_replenishment_suggestions()
    return render_template('replenishment.html', suggestions=suggestions)



@bp.route('/monitoring')
def monitoring():
    alerts = StockMonitor.get_stock_alerts()
    return render_template('monitoring.html', alerts=alerts)



@bp.route('/forecasting')
def forecasting():
    products = Product.query.all()
    current_date = datetime.now()
    
    for product in products:
        # Get historical sales data for the past 12 months
        historical_sales = db.session.query(
            func.sum(Sale.quantity),
            func.strftime('%Y-%m', Sale.sale_date).label('month')
        ).filter(
            Sale.product_id == product.id,
            Sale.sale_date >= (current_date - timedelta(days=365))
        ).group_by('month').all()
        
        # Calculate seasonal trends (quarterly)
        seasonal_data = db.session.query(
            func.sum(Sale.quantity),
            func.strftime('%m', Sale.sale_date).label('month')
        ).filter(
            Sale.product_id == product.id
        ).group_by('month').all()
        
        # Calculate growth pattern
        if historical_sales:
            sales_values = [sale[0] for sale in historical_sales if sale[0]]
            if sales_values:
                growth_rate = (sales_values[-1] - sales_values[0]) / sales_values[0] if sales_values[0] else 0
            else:
                growth_rate = 0
        else:
            growth_rate = 0
            
        # Forecast next month's demand
        avg_monthly_sales = np.mean([sale[0] for sale in historical_sales if sale[0]]) if historical_sales else 0
        seasonal_factor = 1.2 if current_date.month in [11, 12] else 1.0  # Holiday season adjustment
        forecast_demand = avg_monthly_sales * (1 + growth_rate) * seasonal_factor
        
        # Add analysis results to product object
        product.forecast_data = {
            'historical_trend': historical_sales,
            'seasonal_pattern': seasonal_data,
            'growth_rate': growth_rate * 100,  # Convert to percentage
            'forecast_demand': round(forecast_demand, 2),
            'recommendation': get_recommendation(product, forecast_demand)
        }
    
    return render_template('forecasting.html', products=products)

def get_recommendation(product, forecast_demand):
    if product.current_stock < product.minimum_stock:
        urgency = "Immediate"
        action = f"Order {round(forecast_demand * 2 - product.current_stock)} units"
    elif product.current_stock < forecast_demand:
        urgency = "Soon"
        action = f"Consider ordering {round(forecast_demand - product.current_stock)} units"
    else:
        urgency = "Stable"
        action = "Stock levels adequate"
    
    return {
        'urgency': urgency,
        'action': action
    }


@bp.route('/generate_report')
def generate_report():
    products = Product.query.all()
    sales = Sale.query.all()
    pdf = ReportGenerator.generate_inventory_report(products, sales)
    return send_file(
        pdf,
        download_name=f'inventory_report_{datetime.now().strftime("%Y%m%d")}.pdf',
        as_attachment=True
    )