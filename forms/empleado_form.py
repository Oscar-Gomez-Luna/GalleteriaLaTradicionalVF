from wtforms import Form
from wtforms import StringField, EmailField, FloatField, DateField, IntegerField, SelectField
from wtforms import validators

class EmpleadoForm(Form):
    apPaterno = StringField('Apellido Paterno:', [
        validators.InputRequired(message="El apellido paterno es obligatorio."),
        validators.Length(max=20, message="Máximo 20 caracteres.")
    ])
    apMaterno = StringField('Apellido Materno:', [
        validators.InputRequired(message="El apellido materno es obligatorio."),
        validators.Length(max=20, message="Máximo 20 caracteres.")
    ])
    nombre = StringField('Nombre(s):', [
        validators.InputRequired(message="El nombre es obligatorio."),
        validators.Length(max=50, message="Máximo 50 caracteres.")
    ])
    genero = SelectField('Género', choices=[
        ('H', 'Hombre'),
        ('M', 'Mujer'),
        ('O', 'Otro')
    ], validators=[validators.InputRequired(message="El género es obligatorio.")])
    telefono = StringField('Teléfono:', [
        validators.InputRequired(message="El teléfono es obligatorio."),
        validators.Length(min=10, max=10, message="El teléfono debe tener 10 dígitos.")
    ])
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
    email = EmailField('Correo Electrónico:', [
        validators.InputRequired(message="El correo electrónico es obligatorio."),
        validators.Email(message="Ingresa un correo electrónico válido.")
    ])
    fechaNacimiento = DateField('Fecha de Nacimiento:', [
        validators.InputRequired(message="La fecha de nacimiento es obligatoria.")
    ], format='%Y-%m-%d')
    rol = SelectField('Rol:', choices=[
        ('ADMI', 'Administrador'),
        ('CAJA', 'Cajero'),
        ('PROD', 'Producción')
    ], validators=[validators.InputRequired(message="El rol es obligatorio.")])
    curp = StringField('CURP:', [
        validators.InputRequired(message="El CURP es obligatorio."),
        validators.Length(min=18, max=18, message="El CURP debe tener 18 caracteres.")
    ])
    rfc = StringField('RFC:', [
        validators.InputRequired(message="El RFC es obligatorio."),
        validators.Length(min=13, max=13, message="El RFC debe tener 13 caracteres.")
    ])
    salarioBruto = FloatField('Salario Bruto:', [
        validators.InputRequired(message="El salario bruto es obligatorio."),
        validators.NumberRange(min=0, message="El salario no puede ser negativo.")
    ])
    fechaIngreso = DateField('Fecha de Ingreso:', [
        validators.InputRequired(message="La fecha de ingreso es obligatoria.")
    ], format='%Y-%m-%d')

class EmpleadoFormMod(Form):
    apPaterno = StringField('Apellido Paterno:', [
        validators.InputRequired(message="El apellido paterno es obligatorio."),
        validators.Length(max=20, message="Máximo 20 caracteres.")
    ])
    apMaterno = StringField('Apellido Materno:', [
        validators.InputRequired(message="El apellido materno es obligatorio."),
        validators.Length(max=20, message="Máximo 20 caracteres.")
    ])
    nombre = StringField('Nombre(s):', [
        validators.InputRequired(message="El nombre es obligatorio."),
        validators.Length(max=50, message="Máximo 50 caracteres.")
    ])
    genero = SelectField('Género', choices=[
        ('H', 'Hombre'),
        ('M', 'Mujer'),
        ('O', 'Otro')
    ], validators=[validators.InputRequired(message="El género es obligatorio.")])
    telefono = StringField('Teléfono:', [
        validators.InputRequired(message="El teléfono es obligatorio."),
        validators.Length(min=10, max=10, message="El teléfono debe tener 10 dígitos.")
    ])
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
    email = EmailField('Correo Electrónico:', [
        validators.InputRequired(message="El correo electrónico es obligatorio."),
        validators.Email(message="Ingresa un correo electrónico válido.")
    ])
    fechaNacimiento = DateField('Fecha de Nacimiento:', [
        validators.InputRequired(message="La fecha de nacimiento es obligatoria.")
    ], format='%Y-%m-%d')
    nombreUsuario = StringField('Nombre de Usuario', [
        validators.InputRequired(message="El nombre de usuario es obligatorio."),
        validators.Length(max=20, message="Máximo 20 caracteres.")
    ])
    contrasenia = StringField('Contraseña')
    rol = SelectField('Rol:', choices=[
        ('ADMI', 'Administrador'),
        ('CAJA', 'Cajero'),
        ('PROD', 'Producción')
    ], validators=[validators.InputRequired(message="El rol es obligatorio.")])
    curp = StringField('CURP:', [
        validators.InputRequired(message="El CURP es obligatorio."),
        validators.Length(min=18, max=18, message="El CURP debe tener 18 caracteres.")
    ])
    rfc = StringField('RFC:', [
        validators.InputRequired(message="El RFC es obligatorio."),
        validators.Length(min=13, max=13, message="El RFC debe tener 13 caracteres.")
    ])
    salarioBruto = FloatField('Salario Bruto:', [
        validators.InputRequired(message="El salario bruto es obligatorio."),
        validators.NumberRange(min=0, message="El salario no puede ser negativo.")
    ])
    fechaIngreso = DateField('Fecha de Ingreso:', [
        validators.InputRequired(message="La fecha de ingreso es obligatoria.")
    ], format='%Y-%m-%d')