from flask import Flask, render_template, redirect, url_for
from flask_wtf import CSRFProtect
from config import DevelopmentConfig
from extensions import db
from controller.administracion_controller import admin_bp
from controller.portal_controller import portal_cliente_bp

app = Flask(__name__, template_folder='view')
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect(app)

# Registrar Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(portal_cliente_bp)

@app.route('/')
def index():
    return redirect(url_for('administracion.clientes.clientes'))

@app.route('/administracion')
def administracion():
    return render_template('layout_administracion.html')

if __name__ == '__main__': 
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5006)
