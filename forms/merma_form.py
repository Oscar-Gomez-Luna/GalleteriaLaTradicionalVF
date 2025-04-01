from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DateField, TextAreaField
from wtforms import validators

class MermaGalletasForm(FlaskForm):
    cantidad = IntegerField('Cantidad:', [
        validators.InputRequired(message="La cantidad es obligatoria."),
        validators.NumberRange(min=1, message="La cantidad debe ser un número positivo.")
    ])
    
    tipo_merma = SelectField('Tipo de Merma:', choices=[
        ('quebrada', 'Por quiebre'),
        ('caducidad', 'Por caducidad'),
        ('derrame', 'Por derrame'),
        ('daño_produccion', 'Daño en producción')
    ], validators=[
        validators.InputRequired(message="El tipo de merma es obligatorio.")
    ])
    
    fecha = DateField('Fecha de la Merma:', [
        validators.InputRequired(message="La fecha de la merma es obligatoria.")
    ], format='%Y-%m-%d')
    
    descripcion = TextAreaField('Descripción:', [
        validators.Optional(),
        validators.Length(max=500, message="Máximo 500 caracteres.")
    ])
