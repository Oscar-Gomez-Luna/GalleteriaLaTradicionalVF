from flask import Blueprint, render_template, request, redirect, url_for, flash
from controller.recetas_controller import recetas_bp
from controller.cliente_controller import clientes_bp

admin_bp = Blueprint('administracion', __name__, url_prefix='/administracion', template_folder='view')

admin_bp.register_blueprint(recetas_bp)
admin_bp.register_blueprint(clientes_bp)


@admin_bp.route('/')
def administracion():
    return redirect(url_for('administracion.recetas.recetas'))