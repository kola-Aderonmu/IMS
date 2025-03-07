from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io
from datetime import datetime

class ReportGenerator:
    @staticmethod
    def generate_inventory_report(products, sales_data):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph(f"Inventory Report - {datetime.now().strftime('%Y-%m-%d')}", 
                                styles['Heading1']))
        
        # Product Table
        product_data = [['Product', 'Current Stock', 'Minimum Stock', 'Status']]
        for product in products:
            status = 'Low' if product.current_stock <= product.minimum_stock else 'OK'
            product_data.append([
                product.name,
                str(product.current_stock),
                str(product.minimum_stock),
                status
            ])
            
        table = Table(product_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
