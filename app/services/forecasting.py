import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from app.models.sales import Sale

class SalesForecaster:
    @staticmethod
    def predict_next_month_sales(product_id):
        # Get historical sales data
        sales = Sale.query.filter_by(product_id=product_id).all()
        
        if len(sales) < 30:  # Need minimum data for prediction
            return None
            
        # Prepare data for prediction
        sales_data = pd.DataFrame([
            {'date': sale.sale_date, 'quantity': sale.quantity}
            for sale in sales
        ])
        
        sales_data['days_from_start'] = (sales_data['date'] - sales_data['date'].min()).dt.days
        
        # Train model
        model = LinearRegression()
        X = sales_data['days_from_start'].values.reshape(-1, 1)
        y = sales_data['quantity'].values
        
        model.fit(X, y)
        
        # Predict next 30 days
        next_30_days = range(len(sales_data), len(sales_data) + 30)
        predictions = model.predict(pd.DataFrame(next_30_days).values)
        
        return sum(predictions)
