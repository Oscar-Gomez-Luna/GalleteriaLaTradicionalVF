from flask import Flask, render_template, request, redirect, url_for
from extensions import csrf, db
from config import DevelopmentConfig
from controller.controller_administracion import admin_bp
from controller.controller_venta import venta_bp
from controller.portal_controller import portal_cliente_bp
from controller.controller_insumo import insumo_bp
from controller.controller_ordenes import orden_bp
from controller.controller_produccion import produccion_bp
from controller.controller_galletas import galletas_bp
from flask_login import LoginManager
from controller.usuarios_controller import usuarios_bp
from controller.dashboard_controller import dashboard_bp

# Inicializar la aplicación Flask
app = Flask(__name__, template_folder='view')
app.config.from_object(DevelopmentConfig)
db.init_app(app)
csrf.init_app(app)

# Registrar blueprints
app.register_blueprint(admin_bp, url_prefix='/administracion')
app.register_blueprint(venta_bp, url_prefix='/venta')
app.register_blueprint(insumo_bp, url_prefix='/insumos')
app.register_blueprint(orden_bp, url_prefix='/orden')
app.register_blueprint(produccion_bp, url_prefix='/produccion')
app.register_blueprint(portal_cliente_bp, url_prefix='/portal')
app.register_blueprint(galletas_bp, url_prefix='/galletas')
app.register_blueprint(usuarios_bp)
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

login_manager = LoginManager(app)
login_manager.login_view = 'usuarios.index'
login_manager.login_message = 'Tienes que iniciar sesión'

@app.route("/")
def index():
    return render_template('home.html')

@app.errorhandler(404)
def page_notfound(e):
    return render_template("404.html"), 404

@login_manager.user_loader
def load_user(user_id):
    from model.usuario import Usuario
    return db.session.get(Usuario, int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', debug=True, port=3000)
