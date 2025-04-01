from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, EmailField
from wtforms import validators

class ProveedorForm(FlaskForm):
    empresa = StringField('Empresa:', [
        validators.InputRequired(message="El nombre de la empresa es obligatorio."),
        validators.Length(max=100, message="Máximo 100 caracteres.")
    ])
    fechaRegistro = DateField('Fecha de Registro:', [
        validators.InputRequired(message="La fecha de registro es obligatoria.")
    ], format='%Y-%m-%d')
    calle = StringField('Calle:', [
        validators.InputRequired(message="La calle es obligatoria."),
        validators.Length(max=50, message="Máximo 50 caracteres.")
    ])
    numero = IntegerField('Número:', [
        validators.InputRequired(message="El número es obligatorio."),
        validators.NumberRange(min=1, message="El número debe ser positivo.")
    ])
    colonia = StringField('Colonia:', [
        validators.InputRequired(message="La colonia es obligatoria."),
        validators.Length(max=50, message="Máximo 50 caracteres.")
    ])
    codigoPostal = IntegerField('Código Postal:', [
        validators.InputRequired(message="El código postal es obligatorio."),
        validators.NumberRange(min=10000, max=99999, message="El código postal debe tener 5 dígitos.")
    ])
    telefono = StringField('Teléfono:', [
        validators.InputRequired(message="El teléfono es obligatorio."),
        validators.Length(min=10, max=10, message="El teléfono debe tener 10 dígitos.")
    ])
    email = EmailField('Correo Electrónico:', [
        validators.InputRequired(message="El correo electrónico es obligatorio."),
        validators.Email(message="Ingresa un correo electrónico válido.")
    ])
    rfc = StringField('RFC:', [
        validators.InputRequired(message="El RFC es obligatorio."),
        validators.Length(min=12, max=12, message="El RFC debe tener 12 caracteres.")
    ])