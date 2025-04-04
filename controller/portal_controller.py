from flask import Blueprint, render_template, request, redirect, url_for, session, flash
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

portal_cliente_bp = Blueprint('portal_cliente', __name__,
                            url_prefix='/portal',
                            template_folder='view')

# Configuración
MODO_PRUEBA = False  # Cambiar a False en producción
CLIENTE_PRUEBA_ID = 1  # ID del cliente de prueba

def obtener_cliente_desde_usuario(user_id):
    """Obtiene el cliente asociado a un usuario"""
    return Cliente.query.filter_by(idUsuario=user_id).first()

@portal_cliente_bp.route('/')
@login_required
@role_required('CLIE')
def index():
    return render_template('portal/welcome.html')

@portal_cliente_bp.route('/portal-cliente', methods=['GET', 'POST'])
@login_required
@role_required('CLIE')
def portal_cliente():
    # Obtener el cliente actual (real o de prueba)
    cliente = obtener_cliente_actual()
    
    if not cliente:
        flash('No se encontró su perfil de cliente', 'error')
        return redirect(url_for('usuarios.index'))
    
    # Guardar el ID del cliente en sesión
    session['cliente_id'] = cliente.idCliente
    
    # Obtener tipos de galletas para el select
    tipos_galletas = TipoGalleta.query.all()
    
    # Inicializar carrito si no existe para este cliente
    if 'carritos' not in session:
        session['carritos'] = {}
    
    if str(cliente.idCliente) not in session['carritos']:
        session['carritos'][str(cliente.idCliente)] = []
    
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
    
    # Obtener galletas si se seleccionó un tipo
    tipo_seleccionado = request.args.get('tipo_galleta')
    galletas = []
    if tipo_seleccionado:
        galletas = Galleta.query.filter_by(tipo_galleta_id=tipo_seleccionado).all()
    
    # Calcular total del carrito
    carrito = session['carritos'].get(str(cliente.idCliente), [])
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
        # Verificar disponibilidad
        if cantidad > galleta.existencia:
            flash(f'No hay suficiente existencia. Disponibles: {galleta.existencia}', 'error')
            return redirect(url_for('portal_cliente.portal_cliente'))
        
        item = {
            'galleta_id': galleta.id_galleta,
            'nombre': galleta.galleta,
            'tipo': galleta.tipo_galleta.nombre,
            'precio': float(galleta.tipo_galleta.costo),
            'cantidad': cantidad,
            'subtotal': float(galleta.tipo_galleta.costo) * cantidad
        }
        
        # Buscar si ya existe el item en el carrito
        carrito = session['carritos'][str(cliente_id)]
        for i, item_carrito in enumerate(carrito):
            if item_carrito['galleta_id'] == item['galleta_id']:
                # Actualizar cantidad y subtotal
                nueva_cantidad = item_carrito['cantidad'] + cantidad
                if nueva_cantidad > galleta.existencia:
                    flash(f'No hay suficiente existencia. Disponibles: {galleta.existencia}', 'error')
                    return redirect(url_for('portal_cliente.portal_cliente'))
                
                carrito[i]['cantidad'] = nueva_cantidad
                carrito[i]['subtotal'] = item_carrito['precio'] * nueva_cantidad
                break
        else:
            # Si no existe, agregarlo
            carrito.append(item)
        
        session.modified = True
        flash('Producto agregado al carrito', 'success')
    
    return redirect(url_for('portal_cliente.portal_cliente'))

def eliminar_del_carrito(cliente_id):
    galleta_id = int(request.form.get('galleta_id'))
    if 'carritos' in session and str(cliente_id) in session['carritos']:
        session['carritos'][str(cliente_id)] = [item for item in session['carritos'][str(cliente_id)] if item['galleta_id'] != galleta_id]
        session.modified = True
        flash('Producto eliminado del carrito', 'info')
    return redirect(url_for('portal_cliente.portal_cliente'))

def limpiar_carrito(cliente_id):
    if 'carritos' in session and str(cliente_id) in session['carritos']:
        session['carritos'][str(cliente_id)] = []
        session.modified = True
        flash('Carrito vaciado', 'info')
    return redirect(url_for('portal_cliente.portal_cliente'))

@portal_cliente_bp.route('/confirmar-pedido', methods=['POST'])
@login_required
@role_required('CLIE')
def confirmar_pedido():
    cliente = obtener_cliente_actual()
    if not cliente:
        flash('Debe iniciar sesión como cliente para confirmar un pedido', 'error')
        return redirect(url_for('usuarios.index'))
    
    cliente_id = cliente.idCliente
    
    if 'carritos' not in session or str(cliente_id) not in session['carritos'] or not session['carritos'][str(cliente_id)]:
        flash('No hay productos en el carrito', 'error')
        return redirect(url_for('portal_cliente.portal_cliente'))
    
    try:
        # Crear la orden
        nueva_orden = Orden(
            descripcion="Pedido de galletas",
            total=sum(item['subtotal'] for item in session['carritos'][str(cliente_id)]),
            fechaAlta=datetime.now(),
            fechaEntrega=datetime.now() + timedelta(days=3),
            tipoVenta="Portal Cliente",
            cliente_id=cliente.idCliente
        )
        
        db.session.add(nueva_orden)
        db.session.flush()
        
        # Crear los detalles de la orden
        for item in session['carritos'][str(cliente_id)]:
            detalle = DetalleVentaOrden(
                galletas_id=item['galleta_id'],
                cantidad=item['cantidad'],
                subtotal=item['subtotal'],
                orden_id=nueva_orden.id_orden
            )
            db.session.add(detalle)
        
        db.session.commit()
        session['carritos'][str(cliente_id)] = []
        session.modified = True
        
        flash(f'Pedido confirmado con éxito! Número de orden: {nueva_orden.id_orden}', 'success')
        return redirect(url_for('portal_cliente.portal_cliente'))
    
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