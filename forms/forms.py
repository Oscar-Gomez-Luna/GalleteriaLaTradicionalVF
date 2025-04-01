from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, IntegerField, PasswordField, SelectField, DateField
from wtforms import validators
from wtforms.fields import FormField

class RecetaForm(FlaskForm):
    nombreReceta = StringField("Nombre de la receta", [
        validators.DataRequired(message="El campo es requerido")
    ])
    descripcion = TextAreaField("Descripción de la receta", [
        validators.DataRequired(message="El campo es requerido")
    ])
    ingredientes = HiddenField()

    cantidad_galletas = StringField("Cantidad de galletas", [
        validators.DataRequired(message="El campo es requerido")
    ])

class PersonaForm(FlaskForm):
    apPaterno = StringField("Apellido Paterno", [
        validators.DataRequired(message="El campo es requerido")
    ])
    apMaterno = StringField("Apellido Materno", [
        validators.DataRequired(message="El campo es requerido")
    ])
    nombre = StringField("Nombre", [
        validators.DataRequired(message="El campo es requerido")
    ])
    genero = SelectField("Género", choices=[('H', 'Hombre'), ('M', 'Mujer'), ('O', 'Otro')], default='O', coerce=str)
    
    telefono = StringField("Teléfono", [
        validators.DataRequired(message="El campo es requerido"),
        validators.Length(min=10, max=10, message="El teléfono debe tener 10 dígitos")
    ])
    calle = StringField("Calle", [
        validators.DataRequired(message="El campo es requerido")
    ])
    numero = IntegerField("Número", [
        validators.DataRequired(message="El campo es requerido")
    ])
    colonia = StringField("Colonia", [
        validators.DataRequired(message="El campo es requerido")
    ])
    codigoPostal = IntegerField("Código Postal", [
        validators.DataRequired(message="El campo es requerido")
    ])
    email = StringField("Correo Electrónico", [
        validators.DataRequired(message="El campo es requerido"),
        validators.Email(message="Correo no válido")
    ])
    fechaNacimiento = DateField("Fecha de Nacimiento", [
        validators.DataRequired(message="El campo es requerido")
    ], format='%Y-%m-%d')

class UsuarioForm(FlaskForm):
    nombreUsuario = StringField("Nombre de Usuario", [
        validators.DataRequired(message="El campo es requerido")
    ])
    contrasenia = StringField("Contraseña", [
        validators.DataRequired(message="El campo es requerido"),
        validators.Length(min=6, message="La contraseña debe tener al menos 6 caracteres")
    ])

class ClienteForm(FlaskForm):
    idPersona = IntegerField("ID de Persona", [
        validators.DataRequired(message="El campo es requerido")
    ])
    idUsuario = IntegerField("ID de Usuario", [
        validators.DataRequired(message="El campo es requerido")
    ])
    persona = FormField(PersonaForm)  # Subformulario para los campos de persona
    usuario = FormField(UsuarioForm)  # Subformulario para los campos de usuario
