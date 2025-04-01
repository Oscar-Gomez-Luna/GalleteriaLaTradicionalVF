from flask import Flask, render_template
from controller.controller_produccion import produccion_bp
from controller.controller_galletas import galletas_bp
from extensions import db
from config import DevelopmentConfig
from extensions import csrf


app = Flask(__name__, template_folder='view')
app.config.from_object(DevelopmentConfig)
app.config['SECRET_KEY'] = 'clave-secreta-segura'
app.config['WTF_CSRF_ENABLED'] = True

csrf.init_app(app)  # Proteger antes de inicializar DB
db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html", active_page="home")

@app.route("/ventas")
def ventas():
    return render_template("layout_galleteria.html", active_page="ventas")

@app.route("/insumos")
def insumos():
    return render_template("insumos.html", active_page="insumos")

@app.route("/ordenes")
def ordenes():
    return render_template("ordenes.html", active_page="ordenes")

@app.route("/ganancias")
def ganancias():
    return render_template("ganancias.html", active_page="ganancias")

@app.route("/administrador")
def administrador():
    return render_template("administrador.html", active_page="administrador")

# Registro de Blueprints con prefijos correctos
app.register_blueprint(produccion_bp, url_prefix='/produccion')
app.register_blueprint(galletas_bp, url_prefix='/galletas')

# Crear tablas dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True, port=3000)
