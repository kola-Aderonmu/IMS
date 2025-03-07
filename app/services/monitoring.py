from app.models.product import Product

class StockMonitor:
    @staticmethod
    def get_stock_alerts():
        alerts = {
            'critical': [],
            'warning': [],
            'healthy': []
        }
        
        products = Product.query.all()
        
        for product in products:
            if product.current_stock <= product.minimum_stock * 0.5:
                alerts['critical'].append(product)
            elif product.current_stock <= product.minimum_stock:
                alerts['warning'].append(product)
            else:
                alerts['healthy'].append(product)
                
        return alerts

    @staticmethod
    def get_stock_trends():
        # Add stock trend analysis logic here
        return {}
