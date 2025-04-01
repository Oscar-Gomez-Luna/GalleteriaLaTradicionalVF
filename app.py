from flask import Flask, render_template, request, redirect, url_for
from extensions import csrf
from config import DeveplopmentConfig
from extensions import db
from controller.controller_administracion import admin_bp
from controller.controller_venta import venta_bp

app = Flask(__name__)
app.config.from_object(DeveplopmentConfig)
db.init_app(app)
csrf.init_app(app)

app.register_blueprint(admin_bp, url_prefix='/administracion')
app.register_blueprint(venta_bp, url_prefix='/venta')

@app.route("/administracion")
@app.route("/administrador")
def proveedores():
    return redirect(url_for('administracion.proveedor.proveedores'))

@app.route("/")
@app.route("/venta")
@app.route("/ventas")
def ventas():
    return redirect(url_for('venta.ventas'))

if __name__ == '__main__':    
    with app.app_context():
        db.create_all()
    app.run(debug=True)