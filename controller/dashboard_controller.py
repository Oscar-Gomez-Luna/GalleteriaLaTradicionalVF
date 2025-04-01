# controller/dashboard_controller.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from model.usuario import Usuario  # Asegúrate de que esto esté correcto
from model.dashboard_model import get_ventas_diarias, get_productos_mas_vendidos, get_presentaciones_mas_vendidas

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    usuario = current_user
    fechas, totales_ventas = get_ventas_diarias()
    nombres_productos, cantidades_productos = get_productos_mas_vendidos()
    nombres_presentaciones, cantidades_presentaciones = get_presentaciones_mas_vendidas()
    return render_template('dashboard.html',
                          usuario=usuario,
                          fechas=fechas,
                          totales_ventas=totales_ventas,
                          nombres_productos=nombres_productos,
                          cantidades_productos=cantidades_productos,
                          nombres_presentaciones=nombres_presentaciones,
                          cantidades_presentaciones=cantidades_presentaciones)