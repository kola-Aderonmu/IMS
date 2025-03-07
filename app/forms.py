from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    current_stock = IntegerField('Current Stock', validators=[DataRequired()])
    minimum_stock = IntegerField('Minimum Stock', validators=[DataRequired()])
    unit_price = FloatField('Unit Price', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SaleForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Record Sale')
