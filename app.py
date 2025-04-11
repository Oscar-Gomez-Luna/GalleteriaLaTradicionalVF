from flask import Flask, render_template, request, redirect, session, url_for
from extensions import csrf, db
from config import DevelopmentConfig
from controller.controller_administracion import admin_bp
from controller.controller_venta import venta_bp
from controller.portal_controller import portal_cliente_bp
from controller.controller_insumo import insumo_bp
from controller.controller_ordenes import orden_bp
from controller.controller_produccion import produccion_bp
from controller.controller_galletas import galletas_bp
from flask_login import LoginManager, current_user
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

def crear_usuarios_iniciales():
    from model.persona import Persona
    from model.usuario import Usuario
    from model.empleado import Empleado
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    # Verificar si ya existen usuarios de prueba
    if Usuario.query.filter(Usuario.nombreUsuario.in_(['LopezJose', 'GonzalesHugo', 'PerezJuan'])).count() == 0:
        try:
            # Usuario Administrador - LopezJose
            persona_admin = Persona(
                apPaterno='Lopez',
                apMaterno='Jose',
                nombre='Jose',
                genero='M',
                telefono='1234567890',
                email='admin@example.com',
                calle='Calle Admin',
                numero=1,
                colonia='Colonia Admin',
                codigoPostal=12345,
                fechaNacimiento=datetime.strptime('1990-01-01', '%Y-%m-%d').date()
            )
            db.session.add(persona_admin)
            db.session.commit()
            
            usuario_admin = Usuario(
                nombreUsuario='LopezJose',
                contrasenia=generate_password_hash('Sotojose12.'),
                estatus=1,
                rol='ADMS'
            )
            db.session.add(usuario_admin)
            db.session.commit()
            
            empleado_admin = Empleado(
                puesto='Administrador',
                curp='LOJA900101HDFPNSA1',
                rfc='LOJA900101ABC',
                salarioBruto=25000.00,
                fechaIngreso=datetime.now().date(),
                idPersona=persona_admin.idPersona,
                idUsuario=usuario_admin.idUsuario
            )
            db.session.add(empleado_admin)
            
            # Usuario Producción - GonzalesHugo
            persona_prod = Persona(
                apPaterno='Gonzales',
                apMaterno='Martinez',
                nombre='Hugo',
                genero='M',
                telefono='2345678901',
                email='prod@example.com',
                calle='Calle Prod',
                numero=2,
                colonia='Colonia Prod',
                codigoPostal=23456,
                fechaNacimiento=datetime.strptime('1991-02-02', '%Y-%m-%d').date()
            )
            db.session.add(persona_prod)
            db.session.commit()
            
            usuario_prod = Usuario(
                nombreUsuario='GonzalesHugo',
                contrasenia=generate_password_hash('Martinezhugo12.'),
                estatus=1,
                rol='PROD'
            )
            db.session.add(usuario_prod)
            db.session.commit()
            
            empleado_prod = Empleado(
                puesto='Producción',
                curp='GOHU910202HDFPNSA2',
                rfc='GOHU910202ABC',
                salarioBruto=15000.00,
                fechaIngreso=datetime.now().date(),
                idPersona=persona_prod.idPersona,
                idUsuario=usuario_prod.idUsuario
            )
            db.session.add(empleado_prod)
            
            # Usuario Cajero - PerezJuan
            persona_caj = Persona(
                apPaterno='Perez',
                apMaterno='Morales',
                nombre='Juan',
                genero='M',
                telefono='3456789012',
                email='cajero@example.com',
                calle='Calle Cajero',
                numero=3,
                colonia='Colonia Cajero',
                codigoPostal=34567,
                fechaNacimiento=datetime.strptime('1992-03-03', '%Y-%m-%d').date()
            )
            db.session.add(persona_caj)
            db.session.commit()
            
            usuario_caj = Usuario(
                nombreUsuario='PerezJuan',
                contrasenia=generate_password_hash('Moralesjuan12.'),
                estatus=1,
                rol='CAJA'
            )
            db.session.add(usuario_caj)
            db.session.commit()
            
            empleado_caj = Empleado(
                puesto='Cajero',
                curp='PEJU920303HDFPNSA3',
                rfc='PEJU920303ABC',
                salarioBruto=12000.00,
                fechaIngreso=datetime.now().date(),
                idPersona=persona_caj.idPersona,
                idUsuario=usuario_caj.idUsuario
            )
            db.session.add(empleado_caj)
            
            db.session.commit()
            print("Usuarios de prueba creados exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuarios de prueba: {str(e)}")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True, port=3000)
