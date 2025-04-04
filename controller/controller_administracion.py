from flask import Blueprint, redirect, url_for
from controller.controller_empleado import usuario_bp
from controller.controller_proveedor import proovedor_bp
from controller.recetas_controller import recetas_bp
from controller.cliente_controller import clientes_bp
from flask_login import login_required
from extensions import role_required

admin_bp = Blueprint('administracion', __name__, url_prefix='/administracion')

admin_bp.register_blueprint(usuario_bp)
admin_bp.register_blueprint(proovedor_bp)
admin_bp.register_blueprint(recetas_bp)
admin_bp.register_blueprint(clientes_bp)

@admin_bp.route('/')
@login_required
@role_required("ADMI") 
def administracion():
    return redirect(url_for('administracion.proveedor.proveedores'))