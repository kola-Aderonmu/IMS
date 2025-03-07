from flask import Blueprint, render_template, redirect, url_for, flash
from app.models.product import Product
from app.services.replenishment import get_replenishment_suggestions
from app.forms import ProductForm, SaleForm
from app.models.sales import Sale
from flask import send_file
from sqlalchemy import func
from app.services.monitoring import StockMonitor
from app.services.forecasting import SalesForecaster
from app.services.reporting import ReportGenerator
from app import db
from datetime import datetime, timedelta
import json
import plotly
import plotly.express as px
import pandas as pd


bp = Blueprint('main', __name__)


@bp.route('/dashboard')
def dashboard():
    # Calculate total sales for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_sales = db.session.query(func.sum(Sale.quantity)).filter(
        Sale.sale_date >= thirty_days_ago
    ).scalar() or 0

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

    # Create graph data
    if sales_trend:
        graph_json = create_sales_graph(sales_trend)
    else:
        graph_json = None

    return render_template('dashboard.html',
        total_sales=total_sales,
        products=products,
        low_stock_products=low_stock_products,
        total_revenue=total_revenue,
        best_selling_products=best_selling_products,
        out_of_stock=out_of_stock,
        total_inventory_value=total_inventory_value,
        recent_sales=recent_sales,
        graph_json=graph_json
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



@bp.route('/record_sale', methods=['GET', 'POST'])
def record_sale():
    form = SaleForm()
    # Populate product choices
    form.product_id.choices = [(p.id, p.name) for p in Product.query.all()]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if product.current_stock >= form.quantity.data:
            # Create new sale record
            sale = Sale(
                product_id=form.product_id.data,
                quantity=form.quantity.data
            )
            # Update product stock
            product.current_stock -= form.quantity.data
            
            db.session.add(sale)
            db.session.commit()
            flash('Sale recorded successfully!')
            return redirect(url_for('main.index'))
        else:
            flash('Not enough stock available!')
    
    return render_template('record_sale.html', form=form)


@bp.route('/product/<int:product_id>/add-stock', methods=['GET', 'POST'])
def add_stock(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 0))
        if quantity > 0:
            product.current_stock += quantity
            db.session.commit()
            flash(f'Successfully added {quantity} units to {product.name}', 'success')
            return redirect(url_for('main.dashboard'))
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
    forecasting_data = []
    
    for product in products:
        forecasting_data.append({
            'name': product.name,
            'current_stock': product.current_stock,
            'minimum_stock': product.minimum_stock,
            'forecast_value': int(product.current_stock * 1.1),  # 10% increase projection
            'trend': 10  # 10% upward trend
        })
    
    return render_template('forecasting.html', forecasting_data=forecasting_data)



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