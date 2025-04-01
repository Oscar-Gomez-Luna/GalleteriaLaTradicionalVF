import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from forms.usuarios_form import LoginForm, RegisterForm
from model.persona import Persona
from model.usuario import Usuario
from model.cliente import Cliente
from model.verificacion_usuario import VerificacionUsuario
from model.usuario_seguridad import UsuarioSeguridad
from extensions import db
from datetime import datetime, timedelta
import secrets
import requests
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText

# Blueprint para usuarios
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '..', 'view', 'usuarios')
print(f"Template folder configurado como: {TEMPLATE_DIR}")
usuarios_bp = Blueprint('usuarios', __name__, template_folder=TEMPLATE_DIR)

# Configuración
RECAPTCHA_SECRET_KEY = '6Lfzv_gqAAAAALxgoUOobpOFldn0VikXsHcuoGRl'  # Reemplaza con tu clave secreta de reCAPTCHA
UNSAFE_PASSWORDS = [
    'password123',
    '12345678',
    'qwerty123',
    'abc12345',
    'letmein123'
]
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'credentials.json'

# Funciones auxiliares
def validate_password(password):
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe tener al menos 1 letra mayúscula."
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe tener al menos 1 letra minúscula."
    if not re.search(r'\d', password):
        return False, "La contraseña debe tener al menos 1 número."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe tener al menos 1 carácter especial."
    if password.lower() in UNSAFE_PASSWORDS:
        return False, "La contraseña es demasiado común. Elige una más segura."
    return True, "Contraseña válida."

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_email(to, subject, body):
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        print(f"Correo enviado a {to}")
        return True
    except HttpError as error:
        print(f'Error al enviar el correo: {error}')
        return False
    except Exception as e:
        print(f'Error inesperado al enviar el correo: {e}')
        return False

def verify_recaptcha(recaptcha_response):
    url = 'https://www.google.com/recaptcha/api/siteverify'
    payload = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    response = requests.post(url, data=payload)
    result = response.json()
    print("Respuesta de reCAPTCHA:", result)
    return result.get('success', False)

@usuarios_bp.before_request
def make_session_permanent():
    session.permanent = True
    session.permanent_session_lifetime = timedelta(minutes=10)
    if 'last_activity' in session:
        last_activity = session['last_activity']
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        inactivity_duration = datetime.now() - last_activity
        if inactivity_duration > timedelta(minutes=10):
            logout_user()
            session.clear()
            flash('Tu sesión ha expirado por inactividad. Por favor, inicia sesión de nuevo.', 'error')
            return redirect(url_for('usuarios.index'))
    session['last_activity'] = datetime.now().isoformat()

# Rutas
@usuarios_bp.route('/login/')
def index():
    form_login = LoginForm()
    form_register = RegisterForm()
    print(f"Intentando renderizar login.html desde: {os.path.join(TEMPLATE_DIR, 'login.html')}")
    return render_template('login.html', form_login=form_login, form_register=form_register)

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('usuarios.index'))

    form_login = LoginForm()
    form_register = RegisterForm()
    if form_login.validate_on_submit():
        recaptcha_response = request.form.get('g-recaptcha-response')
        print("reCAPTCHA response recibido:", recaptcha_response)
        if not recaptcha_response:
            flash('Por favor, completa el reCAPTCHA.', 'error')
        elif not verify_recaptcha(recaptcha_response):
            flash('Error en la verificación de reCAPTCHA. Intenta de nuevo.', 'error')
        else:
            usuario = Usuario.query.filter_by(nombreUsuario=form_login.username.data).first()
            if usuario and usuario.check_password(form_login.password.data) and usuario.estatus == 1:
                verificacion = VerificacionUsuario.query.filter_by(idUsuario=usuario.idUsuario).first()
                if not verificacion or not verificacion.verificado:
                    flash('Por favor, verifica tu correo antes de iniciar sesión.', 'error')
                else:
                    usuario.ultima_conexion = datetime.now()
                    if usuario.seguridad:
                        usuario.seguridad.failed_login_attempts = 0
                    else:
                        seguridad = UsuarioSeguridad(idUsuario=usuario.idUsuario, failed_login_attempts=0)
                        db.session.add(seguridad)
                    db.session.commit()
                    print(f"Inicio de sesión exitoso. failed_login_attempts reiniciado a: {usuario.seguridad.failed_login_attempts}")
                    login_user(usuario, remember=False, duration=timedelta(minutes=10))
                    session['last_activity'] = datetime.now().isoformat()
                    flash('¡Inicio de sesión exitoso!', 'success')
                    return redirect(url_for('dashboard.dashboard'))
            else:
                if usuario:
                    if not usuario.seguridad:
                        print(f"No existe registro en usuario_seguridad para idUsuario: {usuario.idUsuario}. Creando uno nuevo.")
                        seguridad = UsuarioSeguridad(idUsuario=usuario.idUsuario, failed_login_attempts=0)
                        db.session.add(seguridad)
                        db.session.commit()
                    usuario.seguridad.failed_login_attempts += 1
                    print(f"Intento fallido. Nuevo valor de failed_login_attempts: {usuario.seguridad.failed_login_attempts}")
                    if usuario.seguridad.failed_login_attempts >= 3:
                        usuario.estatus = 0
                        db.session.commit()
                        flash('Cuenta bloqueada por demasiados intentos fallidos. Contacta al soporte.', 'error')
                    else:
                        db.session.commit()
                        flash(f'Usuario o contraseña incorrectos. Intento {usuario.seguridad.failed_login_attempts}/3.', 'error')
                else:
                    flash('Usuario o contraseña incorrectos.', 'error')
    print(f"Intentando renderizar login.html desde: {os.path.join(TEMPLATE_DIR, 'login.html')}")
    return render_template('login.html', form_login=form_login, form_register=form_register)

@usuarios_bp.route('/register', methods=['POST'])
def register():
    form_login = LoginForm()
    form_register = RegisterForm()
    print("Conexión a la base de datos activa:", db.engine)
    print("Datos recibidos:", request.form)
    if form_register.validate_on_submit():
        try:
            is_valid, message = validate_password(form_register.password.data)
            if not is_valid:
                flash(message, 'error')
                return render_template('login.html', form_login=form_login, form_register=form_register)

            if Usuario.query.filter_by(nombreUsuario=form_register.username.data).first():
                flash('El nombre de usuario ya está en uso.', 'error')
            elif Persona.query.filter_by(email=form_register.email.data).first():
                flash('El correo ya está registrado.', 'error')
            else:
                nueva_persona = Persona(
                    apPaterno=form_register.apPaterno.data,
                    apMaterno=form_register.apMaterno.data,
                    nombre=form_register.nombre.data,
                    genero=form_register.genero.data,
                    telefono=form_register.telefono.data,
                    calle=form_register.calle.data,
                    numero=form_register.numero.data,
                    colonia=form_register.colonia.data,
                    codigoPostal=form_register.codigoPostal.data,
                    email=form_register.email.data,
                    fechaNacimiento=form_register.fechaNacimiento.data
                )
                db.session.add(nueva_persona)
                db.session.commit()
                print(f"Persona insertada: {nueva_persona.idPersona}")

                nuevo_usuario = Usuario(
                    nombreUsuario=form_register.username.data,
                    rol='CLIE',
                    estatus=1,
                    ultima_conexion=datetime.now()
                )
                nuevo_usuario.set_password(form_register.password.data)
                db.session.add(nuevo_usuario)
                db.session.commit()
                print(f"Usuario insertado: {nuevo_usuario.idUsuario}")

                nueva_seguridad = UsuarioSeguridad(
                    idUsuario=nuevo_usuario.idUsuario,
                    failed_login_attempts=0,
                    password_last_changed=datetime.now()
                )
                db.session.add(nueva_seguridad)
                print(f"Seguridad insertada: {nueva_seguridad.idUsuarioSeguridad}")

                codigo_verificacion = secrets.token_urlsafe(16)
                nueva_verificacion = VerificacionUsuario(
                    idUsuario=nuevo_usuario.idUsuario,
                    verificado=False,
                    codigo_verificacion=codigo_verificacion,
                    created_at=datetime.now()
                )
                db.session.add(nueva_verificacion)
                print(f"Verificación insertada: {nueva_verificacion.idVerificacion}")

                nuevo_cliente = Cliente(
                    idPersona=nueva_persona.idPersona,
                    idUsuario=nuevo_usuario.idUsuario
                )
                db.session.add(nuevo_cliente)
                db.session.commit()
                print("Cliente insertado")

                verification_url = url_for('usuarios.confirmar_correo', codigo=codigo_verificacion, _external=True)
                email_sent = send_email(nueva_persona.email, "Confirma tu correo - La Tradicional",
                                       f"Gracias por registrarte. Haz clic aquí para verificar tu correo:\n{verification_url}")
                if email_sent:
                    flash('Registro exitoso. Revisa tu correo para verificar tu cuenta.', 'success')
                else:
                    flash('Registro exitoso, pero no se pudo enviar el correo de verificación. Contacta al soporte.', 'warning')
                return redirect(url_for('usuarios.index'))
        except Exception as e:
            db.session.rollback()
            print(f"Error en el registro: {e}")
            flash(f'Error al registrar: {str(e)}', 'error')
    else:
        print("Formulario no válido. Errores:", form_register.errors)
    print(f"Intentando renderizar login.html desde: {os.path.join(TEMPLATE_DIR, 'login.html')}")
    return render_template('login.html', form_login=form_login, form_register=form_register)

@usuarios_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('La contraseña actual es incorrecta.', 'error')
        elif new_password != confirm_password:
            flash('Las nuevas contraseñas no coinciden.', 'error')
        else:
            is_valid, message = validate_password(new_password)
            if not is_valid:
                flash(message, 'error')
            else:
                current_user.set_password(new_password)
                if not current_user.seguridad:
                    seguridad = UsuarioSeguridad(idUsuario=current_user.idUsuario, password_last_changed=datetime.now())
                    db.session.add(seguridad)
                current_user.seguridad.password_last_changed = datetime.now()
                db.session.commit()
                flash('Contraseña cambiada exitosamente.', 'success')
                return redirect(url_for('dashboard.dashboard'))  # Endpoint correcto
    return render_template('cambiarContraseña.html')

@usuarios_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('usuarios.index'))

@usuarios_bp.route('/confirmar_correo/<codigo>')
def confirmar_correo(codigo):
    verificacion = VerificacionUsuario.query.filter_by(codigo_verificacion=codigo).first()
    if verificacion:
        if datetime.now() > verificacion.created_at + timedelta(minutes=10):
            db.session.delete(verificacion)
            db.session.commit()
            flash('El enlace de verificación ha expirado. Regístrate de nuevo.', 'error')
        else:
            verificacion.verificado = True
            verificacion.codigo_verificacion = None
            db.session.commit()
            flash('¡Correo verificado exitosamente! Ahora puedes iniciar sesión.', 'success')
    else:
        flash('El enlace de verificación es inválido o ha expirado.', 'error')
    return redirect(url_for('usuarios.index'))

@usuarios_bp.route('/test_insert', methods=['GET'])
def test_insert():
    try:
        nueva_persona = Persona(
            apPaterno="Test",
            apMaterno="Test",
            nombre="Test",
            genero="O",
            telefono="1234567890",
            calle="Calle Test",
            numero=1,
            colonia="Colonia Test",
            codigoPostal=12345,
            email="test@example.com",
            fechaNacimiento=datetime.now().date()
        )
        db.session.add(nueva_persona)
        db.session.commit()
        print("Inserción de prueba exitosa")
        return "Inserción OK"
    except Exception as e:
        db.session.rollback()
        print(f"Error en inserción de prueba: {e}")
        return f"Error: {e}"