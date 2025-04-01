from flask import Flask, render_template, request, redirect, url_for
from extensions import csrf, db
from config import DevelopmentConfig
from controller.controller_insumo import insumo_bp
from controller.controller_ordenes import orden_bp

app = Flask(__name__, template_folder='view') 

app.config.from_object(DevelopmentConfig)
db.init_app(app)
csrf.init_app(app)


app.register_blueprint(insumo_bp, url_prefix='/insumos')
app.register_blueprint(orden_bp, url_prefix='/orden')

@app.route("/")
def index():
    return redirect(url_for('insumo.insumos'))

@app.route("/galletas")
def galletas():
    return render_template("layout_clientes.html", active_page="galletas")

@app.route("/ventas")
def ventas():
    return render_template("layout_clientes.html", active_page="ventas")

@app.route("/produccion")
def produccion():
    return render_template("layout_login.html", active_page="produccion")

@app.route("/ordenes")
def ordenes():
    return render_template("ordenes.html", active_page="ordenes")

@app.route("/ganancias")
def ganancias():
    return render_template("layout_clientes.html", active_page="ganancias")

@app.route("/administracion")
def administracion():
    return render_template("layout_clientes.html", active_page="administracion")

@app.route("/proveedores")
def proveedores():
    return render_template("layout_clientes.html", active_page="proveedores")


@app.route("/clientes")
def clientes():
    return render_template("layout_clientes.html", active_page="clientes")

@app.route("/recetas")
def recetas():
    return render_template("layout_clientes.html", active_page="recetas")

if __name__ == '__main__':    
    with app.app_context():
        db.create_all()
    app.run(debug=True)