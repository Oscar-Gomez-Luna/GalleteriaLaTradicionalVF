from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DecimalField, SubmitField
from wtforms import validators
from wtforms.validators import DataRequired, NumberRange

class VentaForm(FlaskForm):
    tipo_venta = SelectField(
        'Tipo de venta',
        choices=[
            (1, 'Unidad'),
            (2, 'Caja De Kilo'),
            (3, 'Caja De 700 Gramos'),
            (1, 'Por Peso'),
            (1, 'Por Cantidad Monetaria')
        ],
        validators=[validators.InputRequired(message="Debe seleccionar un tipo de venta")]
    )
    cantidad = IntegerField(
        'Cantidad',
        validators=[
            DataRequired(message="Ingrese la cantidad"),
            NumberRange(min=1, message="La cantidad debe ser al menos 1")
        ]
    )