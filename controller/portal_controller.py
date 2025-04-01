from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from model.tipo_galleta import db, TipoGalleta
from model.galleta import db, Galleta
from model.orden import db, Orden
from model.detalle_orden import DetalleVentaOrden
from model.usuario import db, Usuario
from model.cliente import db, Cliente
from model.persona import db, Persona

portal_cliente_bp = Blueprint('portal_cliente', __name__, 
                            url_prefix='/portal',
                            template_folder='view')

# Configuración
MODO_PRUEBA = True  # Cambiar a False en producción
CLIENTE_PRUEBA_ID = 1 # ID del cliente de prueba

@portal_cliente_bp.route('/')
def index():
    return render_template('portal/welcome.html')

@portal_cliente_bp.route('/portal-cliente', methods=['GET', 'POST'])
def portal_cliente():
    # Verificar si hay cliente logeado o usar modo prueba
    if 'cliente_id' not in session and not MODO_PRUEBA:
        flash('Debe iniciar sesión para acceder al portal', 'error')
        return redirect(url_for('auth.login'))  # Asume que tienes una ruta de login
    
    # Obtener el ID del cliente actual (real o de prueba)
    cliente_id = session.get('cliente_id', CLIENTE_PRUEBA_ID) if MODO_PRUEBA else session.get('cliente_id')
    
    # Obtener tipos de galletas para el select
    tipos_galletas = TipoGalleta.query.all()
    
    # Inicializar carrito si no existe para este cliente
    if 'carritos' not in session:
        session['carritos'] = {}
    
    if str(cliente_id) not in session['carritos']:
        session['carritos'][str(cliente_id)] = []
    
    # Procesar formulario cuando se envía
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'agregar':
            return agregar_al_carrito(cliente_id)
        elif action == 'eliminar':
            return eliminar_del_carrito(cliente_id)
        elif action == 'limpiar':
            return limpiar_carrito(cliente_id)
        
        return redirect(url_for('portal_cliente.portal_cliente'))
    
    # Obtener galletas si se seleccionó un tipo
    tipo_seleccionado = request.args.get('tipo_galleta')
    galletas = []
    if tipo_seleccionado:
        galletas = Galleta.query.filter_by(tipo_galleta_id=tipo_seleccionado).all()
    
    # Calcular total del carrito
    carrito = session['carritos'].get(str(cliente_id), [])
    total = sum(item['subtotal'] for item in carrito)
    
    return render_template('portal/portal_cliente.html',
                         tipos_galletas=tipos_galletas,
                         galletas=galletas,
                         carrito=carrito,
                         total=total,
                         modo_prueba=MODO_PRUEBA)

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
            'tipo': galleta.tipo_galleta_rel.nombre,
            'precio': float(galleta.tipo_galleta_rel.costo),
            'cantidad': cantidad,
            'subtotal': float(galleta.tipo_galleta_rel.costo) * cantidad
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

def obtener_cliente_actual():
    """Obtiene el cliente actual (real o de prueba)"""
    if not MODO_PRUEBA and 'cliente_id' in session:
        # Modo producción con cliente real
        return Cliente.query.get(session['cliente_id'])
    else:
        # Modo prueba con cliente temporal
        return crear_cliente_temporal()

def crear_cliente_temporal():
    """Función para crear un cliente temporal si no existe"""
    cliente_temporal = Cliente.query.get(CLIENTE_PRUEBA_ID)
    
    if not cliente_temporal and MODO_PRUEBA:
        try:
            # Crear persona temporal
            persona = Persona(
                apPaterno='Temporal',
                apMaterno='Cliente',
                nombre='Invitado',
                genero='O',
                telefono='0000000000',
                calle='Desconocida',
                numero=0,
                colonia='Desconocida',
                codigoPostal=00000,
                email='invitado@temporal.com',
                fechaNacimiento=datetime.now().date()
            )
            db.session.add(persona)
            db.session.flush()
            
            # Crear usuario temporal
            usuario = Usuario(
                nombreUsuario='invitado_temp',
                estatus=1,
                contrasenia='temp1234',
                rol='CLIE'
            )
            db.session.add(usuario)
            db.session.flush()
            
            # Crear cliente temporal
            cliente_temporal = Cliente(
                idPersona=persona.idPersona,
                idUsuario=usuario.idUsuario
            )
            db.session.add(cliente_temporal)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Error al crear cliente temporal', 'error')
            raise e
    
    return cliente_temporal

@portal_cliente_bp.route('/confirmar-pedido', methods=['POST'])
def confirmar_pedido():
    cliente_id = session.get('cliente_id', CLIENTE_PRUEBA_ID) if MODO_PRUEBA else session.get('cliente_id')
    
    if 'carritos' not in session or str(cliente_id) not in session['carritos'] or not session['carritos'][str(cliente_id)]:
        flash('No hay productos en el carrito', 'error')
        return redirect(url_for('portal_cliente.portal_cliente'))
    
    try:
        # Obtener cliente actual (real o temporal)
        cliente = obtener_cliente_actual()
        if not cliente:
            flash('No se pudo identificar al cliente', 'error')
            return redirect(url_for('portal_cliente.portal_cliente'))
        
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
def mis_pedidos():
    # Obtener cliente actual
    cliente = obtener_cliente_actual()
    if not cliente:
        flash('No se pudo identificar al cliente', 'error')
        return redirect(url_for('portal_cliente.portal_cliente'))
    
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
                'tipo': galleta.tipo_galleta_rel.nombre,
                'cantidad': detalle.cantidad,
                'subtotal': f"${detalle.subtotal:.2f}"
            })
        
        pedidos.append(pedido)
    
    return render_template('portal/mis_pedidos.html', pedidos=pedidos)