# forms/usuarios_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from model.persona import Persona
from model.usuario import Usuario

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8, max=16)])
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8, max=16)])
    apPaterno = StringField('Apellido Paterno', validators=[DataRequired(), Length(max=20)])
    apMaterno = StringField('Apellido Materno', validators=[DataRequired(), Length(max=20)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    genero = SelectField('Género', choices=[('H', 'Hombre'), ('M', 'Mujer'), ('O', 'Otro')], validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(min=10, max=10)])
    calle = StringField('Calle', validators=[DataRequired(), Length(max=50)])
    numero = IntegerField('Número', validators=[DataRequired()])
    colonia = StringField('Colonia', validators=[DataRequired(), Length(max=50)])
    codigoPostal = IntegerField('Código Postal', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=100)])
    fechaNacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        usuario = Usuario.query.filter_by(nombreUsuario=username.data).first()
        if usuario:
            raise ValidationError('El nombre de usuario ya está en uso.')

    def validate_email(self, email):
        persona = Persona.query.filter_by(email=email.data).first()
        if persona:
            raise ValidationError('El correo ya está registrado.')