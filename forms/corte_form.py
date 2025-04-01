from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, StringField
from wtforms import validators

class CorteCajaForm(FlaskForm):
    fecha = DateField('Fecha:', [
        validators.InputRequired(message="La fecha del corte es obligatoria.")
    ], format='%Y-%m-%d')
    
    cantidadCaja = DecimalField('Cantidad en Caja:', [
        validators.InputRequired(message="La cantidad en caja es obligatoria."),
        validators.NumberRange(min=0, message="La cantidad en caja debe ser mayor o igual a 0.")
    ], places=2)
    
    observaciones = StringField('Observaciones:', [
        validators.Length(max=200, message="Las observaciones pueden tener un máximo de 200 caracteres.")
    ])