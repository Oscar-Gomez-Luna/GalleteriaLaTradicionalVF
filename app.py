# app.py
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import DevelopmentConfig
from controller.usuarios_controller import usuarios_bp
from controller.dashboard_controller import dashboard_bp
from extensions import db, csrf

# Inicializar la aplicación Flask
app = Flask(__name__, template_folder='view')  # Especificamos que las plantillas están en 'view/'
app.config.from_object(DevelopmentConfig)

# Asegurarse de que la SECRET_KEY esté definida
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Reemplaza con una clave secreta única y segura

# Inicializar extensiones con la app
db.init_app(app)
csrf.init_app(app)

# Inicializar otras extensiones
login_manager = LoginManager(app)
login_manager.login_view = 'usuarios.index'  # Cambiado a usuarios.index, que ahora es /login/

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Registrar Blueprints
app.register_blueprint(usuarios_bp)
app.register_blueprint(dashboard_bp)

# Configurar Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from model.usuario import Usuario  # Asegúrate de que esto esté correcto
    return db.session.get(Usuario, int(user_id))  # Usar db.session.get en lugar de query.get

# Ruta raíz para redirigir a /login/
@app.route('/')
def index():
    return redirect(url_for('usuarios.index'))  # Esto redirigirá a /login/

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)