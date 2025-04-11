from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime, timedelta
from model.tipo_galleta import db, TipoGalleta
from model.galleta import db, Galleta
from model.orden import db, Orden
from model.detalle_venta_orden import DetalleVentaOrden
from model.usuario import db, Usuario
from model.cliente import db, Cliente
from model.persona import db, Persona
from flask_login import login_required, current_user
from extensions import role_required
import json

portal_cliente_bp = Blueprint('portal_cliente', __name__,
                            url_prefix='/portal',
                            template_folder='view')

# Configuración
MODO_PRUEBA = False  # Cambiar a False en producción
CLIENTE_PRUEBA_ID = 1  # ID del cliente de prueba

def obtener_cliente_desde_usuario(user_id):
    """Obtiene el cliente asociado a un usuario"""
    return Cliente.query.filter_by(idUsuario=user_id).first()

def get_cliente_carrito(cliente_id):
    """Obtiene el carrito del cliente desde las cookies"""
    carrito_cookie = request.cookies.get(f'carrito_{cliente_id}')
    return json.loads(carrito_cookie) if carrito_cookie else []

def set_cliente_carrito(cliente_id, carrito):
    """Guarda el carrito del cliente en las cookies"""
    response = make_response(redirect(url_for('portal_cliente.portal_cliente')))
    response.set_cookie(
        f'carrito_{cliente_id}',
        json.dumps(carrito),
        max_age=30*24*60*60,  # 30 días de duración
        httponly=True,
        secure=True,  # Solo para HTTPS
        samesite='Lax'
    )
    return response

@portal_cliente_bp.route('/')
@login_required
@role_required('CLIE')
def index():
    cliente = obtener_cliente_desde_usuario(current_user.idUsuario)
    if cliente and cliente.persona:
        nombre_completo = f"{cliente.persona.nombre} {cliente.persona.apPaterno}"
    else:
        nombre_completo = current_user.nombre
    
    return render_template('portal/welcome.html', nombre_completo=nombre_completo)

@portal_cliente_bp.route('/portal-cliente', methods=['GET', 'POST'])
@login_required
@role_required('CLIE')
def portal_cliente():
    # Obtener el cliente actual (real o de prueba)
    cliente = obtener_cliente_actual()
    
    if not cliente:
        flash('No se encontró su perfil de cliente', 'error')
        return redirect(url_for('usuarios.index'))
    
    # Obtener carrito desde cookies
    carrito = get_cliente_carrito(cliente.idCliente)
    
    # Procesar formulario cuando se envía
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'agregar':
            return agregar_al_carrito(cliente.idCliente)
        elif action == 'eliminar':
            return eliminar_del_carrito(cliente.idCliente)
        elif action == 'limpiar':
            return limpiar_carrito(cliente.idCliente)
        
        return redirect(url_for('portal_cliente.portal_cliente'))
    
    from sqlalchemy.orm import joinedload
    
    # Obtener tipos de galletas para el select
    tipos_galletas = TipoGalleta.query.all()
    
    # Obtener galletas basadas en el filtro o todas si no hay filtro
    tipo_seleccionado = request.args.get('tipo_galleta')
    galletas = Galleta.query.options(joinedload(Galleta.galletas_receta))
    
    if tipo_seleccionado:
        galletas = galletas.filter_by(tipo_galleta_id=tipo_seleccionado)
    
    galletas = galletas.all()
    
    # Calcular total del carrito
    total = sum(item['subtotal'] for item in carrito)
    
    return render_template('portal/portal_cliente.html',
                         tipos_galletas=tipos_galletas,
                         galletas=galletas,
                         carrito=carrito,
                         total=total,
                         modo_prueba=MODO_PRUEBA)

def obtener_id_cliente_actual():
    """Obtiene el ID del cliente actual según el modo de operación"""
    if MODO_PRUEBA:
        return CLIENTE_PRUEBA_ID
    
    if not current_user.is_authenticated:
        return None
    
    # Obtener el cliente asociado al usuario actual
    cliente = obtener_cliente_desde_usuario(current_user.idUsuario)
    return cliente.idCliente if cliente else None

def obtener_cliente_actual():
    """Obtiene el objeto Cliente actual según el modo de operación"""
    if MODO_PRUEBA:
        return Cliente.query.get(CLIENTE_PRUEBA_ID)
    
    if not current_user.is_authenticated:
        return None
    
    # Obtener el cliente asociado al usuario actual
    return obtener_cliente_desde_usuario(current_user.idUsuario)

def agregar_al_carrito(cliente_id):
    galleta_id = request.form.get('galleta_id')
    cantidad = int(request.form.get('cantidad', 1))
    
    if not galleta_id:
        flash('Debe seleccionar una galleta', 'error')
        return redirect(url_for('portal_cliente.portal_cliente'))
    
    galleta = Galleta.query.get(galleta_id)
    if galleta:
        # Obtener carrito actual
        carrito = get_cliente_carrito(cliente_id)
        
        # Buscar si ya existe el item en el carrito
        item_existente = next((item for item in carrito if item['galleta_id'] == galleta_id), None)
        
        if item_existente:
            # Actualizar cantidad
            nueva_cantidad = item_existente['cantidad'] + cantidad
            
            item_existente['cantidad'] = nueva_cantidad
            item_existente['subtotal'] = float(galleta.tipo_galleta.costo) * nueva_cantidad
        else:
            # Agregar nuevo item
            carrito.append({
                'galleta_id': galleta.id_galleta,
                'nombre': galleta.galleta,
                'tipo': galleta.tipo_galleta.nombre,
                'precio': float(galleta.tipo_galleta.costo),
                'cantidad': cantidad,
                'subtotal': float(galleta.tipo_galleta.costo) * cantidad
            })
        
        # Guardar carrito actualizado
        response = set_cliente_carrito(cliente_id, carrito)
        flash('Producto agregado al carrito', 'success')
        return response
    
    return redirect(url_for('portal_cliente.portal_cliente'))

def eliminar_del_carrito(cliente_id):
    galleta_id = int(request.form.get('galleta_id'))
    
    # Obtener carrito actual
    carrito = get_cliente_carrito(cliente_id)
    
    # Filtrar para eliminar el item
    nuevo_carrito = [item for item in carrito if item['galleta_id'] != galleta_id]
    
    # Guardar carrito actualizado
    response = set_cliente_carrito(cliente_id, nuevo_carrito)
    flash('Producto eliminado del carrito', 'info')
    return response

def limpiar_carrito(cliente_id):
    response = make_response(redirect(url_for('portal_cliente.portal_cliente')))
    response.set_cookie(
        f'carrito_{cliente_id}',
        '',
        expires=0  # Eliminar la cookie
    )
    flash('Carrito vaciado', 'info')
    return response

@portal_cliente_bp.route('/confirmar-pedido', methods=['POST'])
@login_required
@role_required('CLIE')
def confirmar_pedido():
    cliente = obtener_cliente_actual()
    if not cliente:
        flash('Debe iniciar sesión como cliente para confirmar un pedido', 'error')
        return redirect(url_for('usuarios.index'))
    
    # Obtener carrito actual
    carrito = get_cliente_carrito(cliente.idCliente)
    
    if not carrito:
        flash('No hay productos en el carrito', 'error')
        return redirect(url_for('portal_cliente.portal_cliente'))
    
    try:
        # Verificar disponibilidad antes de confirmar
        for item in carrito:
            galleta = Galleta.query.get(item['galleta_id'])
                    
        # Crear la orden
        nueva_orden = Orden(
            descripcion="Pedido de galletas",
            total=sum(item['subtotal'] for item in carrito),
            fechaAlta=datetime.now(),
            fechaEntrega=datetime.now() + timedelta(days=3),
            tipoVenta="Portal Cliente",
            cliente_id=cliente.idCliente
        )
        
        db.session.add(nueva_orden)
        db.session.flush()
        
        # Crear los detalles de la orden
        for item in carrito:
            detalle = DetalleVentaOrden(
                galletas_id=item['galleta_id'],
                cantidad=item['cantidad'],
                subtotal=item['subtotal'],
                orden_id=nueva_orden.id_orden
            )
            db.session.add(detalle)
            
            # Actualizar existencia
            galleta = Galleta.query.get(item['galleta_id'])
            galleta.existencia -= item['cantidad']
        
        db.session.commit()
        
        # Limpiar carrito después de confirmar
        response = make_response(redirect(url_for('portal_cliente.portal_cliente')))
        response.set_cookie(
            f'carrito_{cliente.idCliente}',
            '',
            expires=0
        )
        flash(f'Pedido confirmado con éxito! Número de orden: {nueva_orden.id_orden}', 'success')
        return response
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error al confirmar el pedido: {str(e)}', 'error')
        return redirect(url_for('portal_cliente.portal_cliente'))

@portal_cliente_bp.route('/mis-pedidos')
@login_required
@role_required('CLIE')
def mis_pedidos():
    cliente = obtener_cliente_actual()
    if not cliente:
        flash('Debe iniciar sesión como cliente para ver sus pedidos', 'error')
        return redirect(url_for('usuarios.index'))
    
    cliente_id = cliente.idCliente
    
    # Obtener órdenes del cliente
    ordenes = Orden.query.filter_by(cliente_id=cliente.idCliente)\
                       .order_by(Orden.fechaAlta.desc())\
                       .all()
    
    # Preparar datos para la vista
    pedidos = []
    for orden in ordenes:
        pedido = {
            'id': orden.id_orden,
            'fecha': orden.fechaAlta.strftime('%d/%m/%Y %H:%M'),
            'entrega': orden.fechaEntrega.strftime('%d/%m/%Y'),
            'total': f"${orden.total:.2f}",
            'detalles': []
        }
        
        # Agregar detalles de cada galleta
        for detalle in orden.detalles:
            galleta = detalle.galleta
            pedido['detalles'].append({
                'nombre': galleta.galleta,
                'tipo': galleta.tipo_galleta.nombre,
                'cantidad': detalle.cantidad,
                'subtotal': f"${detalle.subtotal:.2f}"
            })
        
        pedidos.append(pedido)
    
    return render_template('portal/mis_pedidos.html', pedidos=pedidos)