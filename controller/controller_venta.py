from flask import Blueprint, redirect, url_for, render_template, request, session, flash, jsonify, make_response
from model.venta import Venta
from datetime import datetime, date
import pdfkit
import base64
from io import BytesIO
from forms.venta_form import VentaForm
from forms.corte_form import CorteCajaForm
from extensions import db
from model.tipo_galleta import TipoGalleta
from model.detalle_venta import LoteGalletas
from model.galleta import Galleta
from model.receta import Receta
from flask_login import login_required
from extensions import role_required
from model.merma_galleta import MermaGalleta
from flask_login import current_user
from forms.merma_form import MermaGalletasForm
from model.persona import Persona
from model.usuario import Usuario
from model.cliente import Cliente
from model.orden import Orden
from model.detalle_venta_orden import DetalleVentaOrden
from model.solicitud_produccion import SolicitudProduccion
from model.corte_caja import CorteCaja
from model.venta import Venta
from model.detalle_venta import DetalleVentaGalletas

venta_bp = Blueprint('venta', __name__, url_prefix='/venta')


@venta_bp.route("/")
@venta_bp.route("/catálago", methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "CAJA") 
def ventas():
    form = VentaForm(request.form)
    ventas = Venta.query.all()
    return render_template("ventas/ventas.html", active_page="ventas", ventas=ventas, form=form, usuario=current_user)

@venta_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "CAJA") 
def registrar_venta():
    form = VentaForm(request.form)

    if 'detalle_venta' not in session:
        session['detalle_venta'] = []

    if request.method == 'POST' and form.validate():
        tipo_galleta_id = request.form.get('tipo_galleta')
        cantidad = form.cantidad.data

        try:
            cantidad = int(cantidad)
            tipo_galleta_id = int(tipo_galleta_id)
        except ValueError:
            flash("Error: Datos inválidos.", "danger")
            return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                detalle_venta=session['detalle_venta'])

        # Calcular la cantidad total ya reservada para esta galleta
        cantidad_reservada = sum(
            item["cantidad"] for item in session['detalle_venta'] 
            if item["id_galleta"] == tipo_galleta_id
        )

        # lotes válidos ordenados por fecha (más antiguos primero)
        lotes_disponibles = (LoteGalletas.query
                            .filter(LoteGalletas.galleta_id == tipo_galleta_id)
                            .filter(LoteGalletas.existencia > 0)
                            .order_by(LoteGalletas.fechaCaducidad.asc())
                            .all())

        if not lotes_disponibles:
            flash("Error: No hay lotes disponibles para esta galleta.", "danger")
            return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                detalle_venta=session['detalle_venta'])

        # Calcular existencia total disponible
        existencia_total = sum(lote.existencia for lote in lotes_disponibles)

        # Validar que haya suficiente existencia considerando lo reservado
        if (cantidad + cantidad_reservada) > existencia_total:
            disponible = existencia_total - cantidad_reservada
            flash(f"Error: No hay suficiente existencia. Disponible: {max(0, disponible)}", "danger")
            return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                detalle_venta=session['detalle_venta'])

        # Obtener la galleta para el precio
        tipo_galleta = Galleta.query.get(tipo_galleta_id)
        if not tipo_galleta:
            flash("Error: La galleta seleccionada no existe.", "danger")
            return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                detalle_venta=session['detalle_venta'])

        precio = tipo_galleta.tipo.costo
        subtotal = cantidad * precio

        # Crear lista de lotes
        lotes_asignados = []
        cantidad_restante = cantidad
        
        # calcular disponibilidad por lote
        lotes_con_disponibilidad = []
        for lote in lotes_disponibles:
            # Calcular reservas existentes para este lote
            reservas_lote = sum(
                lote_item["cantidad"] 
                for item in session['detalle_venta'] 
                for lote_item in item.get("lotes", [])
                if lote_item["lote_id"] == lote.id_lote
            )
            disponible = lote.existencia - reservas_lote
            if disponible > 0:
                lotes_con_disponibilidad.append({
                    "lote": lote,
                    "disponible": disponible
                })

        # Asignar cantidades a lotes
        for lote_info in lotes_con_disponibilidad:
            if cantidad_restante <= 0:
                break
                
            lote = lote_info["lote"]
            disponible = lote_info["disponible"]
            
            cantidad_a_usar = min(cantidad_restante, disponible)
            
            lotes_asignados.append({
                "lote_id": lote.id_lote,
                "cantidad": cantidad_a_usar,
                "fecha_caducidad": lote.fechaCaducidad.strftime('%Y/%m/%d')
            })
            
            cantidad_restante -= cantidad_a_usar
            
        # Buscar si ya existe este tipo de galleta
        item_existente = None
        for item in session['detalle_venta']:
            if item["id_galleta"] == tipo_galleta_id:
                item_existente = item
                break
        
        if item_existente:
            # Actualizar el item
            item_existente["cantidad"] += cantidad
            item_existente["subtotal"] = float(item_existente["cantidad"] * precio)
            
            # Agregar los lotes nuevos a los existentes
            for lote_nuevo in lotes_asignados:
                lote_encontrado = False
                for lote_existente in item_existente["lotes"]:
                    if lote_existente["lote_id"] == lote_nuevo["lote_id"]:
                        # Si ya existe el lote, solo sumamos la cantidad
                        lote_existente["cantidad"] += lote_nuevo["cantidad"]
                        lote_encontrado = True
                        break
                
                # Si no se encontró el lote, lo agregamos
                if not lote_encontrado:
                    item_existente["lotes"].append(lote_nuevo)
        else:
            
            nueva_venta = {
                "id_galleta": tipo_galleta_id,
                "nombre": tipo_galleta.galleta,
                "tipo": tipo_galleta.tipo.nombre,
                "cantidad": cantidad,
                "precio_unitario": float(precio),
                "subtotal": float(subtotal),
                "lotes": lotes_asignados
            }
            session['detalle_venta'].append(nueva_venta)
        
        session.modified = True
        return redirect(url_for('venta.registrar_venta'))

    return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                        detalle_venta=session['detalle_venta'])

@venta_bp.route('/finalizar', methods=['POST'])
@login_required
@role_required("ADMS", "CAJA") 
def finalizar_venta():
    if 'detalle_venta' not in session or not session['detalle_venta']:
        flash("Error: No hay productos en la venta.", "danger")
        return redirect(url_for('venta.registrar_venta'))

    try:
        tipo_venta = "Punto de Venta"
        total = sum(item['subtotal'] for item in session['detalle_venta'])
        ahora = datetime.now()
        fecha_venta = ahora.date()
        hora_venta = ahora.time()
        ticket = f"TK-{ahora.strftime('%Y%m%d%H%M%S')}"

        # Registrar venta
        nueva_venta = Venta(
            total=total,
            fecha=fecha_venta,
            hora=hora_venta,
            ticket=ticket,
            tipoVenta=tipo_venta
        )
        db.session.add(nueva_venta)
        db.session.flush()

        # Registrar detalles y actualizar existencias
        for detalle in session['detalle_venta']:
            for lote_info in detalle['lotes']:
                # Registrar detalle por cada lote usado
                nuevo_detalle = DetalleVentaGalletas(
                    venta_id=nueva_venta.id_venta,
                    lote_id=lote_info['lote_id'],
                    cantidad=lote_info['cantidad'],
                    subtotal=lote_info['cantidad'] * detalle['precio_unitario']
                )
                db.session.add(nuevo_detalle)

                # Actualizar existencia real
                lote = LoteGalletas.query.get(lote_info['lote_id'])
                if lote:
                    lote.existencia -= lote_info['cantidad']
                    lote.galleta.existencia -= lote_info['cantidad']
                    if lote.existencia < 0:
                        db.session.rollback()
                        flash(f"Error: Existencia insuficiente en lote {lote.id_lote}. La venta no se completó.", "danger")
                        return redirect(url_for('venta.registrar_venta'))

        db.session.commit()
        venta_id = nueva_venta.id_venta
        session.pop('detalle_venta', None)
        session.modified = True

        flash("Venta registrada exitosamente!", "success")
        return redirect(url_for('venta.generar_ticket', venta_id=venta_id))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar la venta: {str(e)}", "danger")
        return redirect(url_for('venta.registrar_venta'))
    
@venta_bp.route("/detalles", methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "CAJA") 
def detalles_venta():
    if request.method == 'GET':
        id_venta = request.args.get('idVenta')
        
        # Consulta principal para obtener la venta
        venta = db.session.query(Venta).filter(Venta.id_venta == id_venta).first()
        
        # obtener los detalles con información relacionada
        detalles_query = db.session.query(
            DetalleVentaGalletas,
            Galleta.galleta,
            TipoGalleta.nombre.label('tipo_galleta'),
            TipoGalleta.costo.label('precio_unitario')
        ).join(
            LoteGalletas, DetalleVentaGalletas.lote_id == LoteGalletas.id_lote
        ).join(
            Galleta, LoteGalletas.galleta_id == Galleta.id_galleta
        ).join(
            TipoGalleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta
        ).filter(
            DetalleVentaGalletas.venta_id == id_venta
        ).all()
        
        # Agrupar por tipo de galleta
        galletas_agrupadas = {}
        for detalle, galleta_nombre, tipo_galleta, precio_unitario in detalles_query:
            # Crear una clave única para cada tipo de galleta
            clave = (galleta_nombre, tipo_galleta, precio_unitario)
            
            if clave not in galletas_agrupadas:
                galletas_agrupadas[clave] = {
                    'galleta': galleta_nombre,
                    'tipo_galleta': tipo_galleta,
                    'precio_unitario': precio_unitario,
                    'cantidad': 0,
                    'subtotal': 0
                }
            
            # Sumar la cantidad y el subtotal
            galletas_agrupadas[clave]['cantidad'] += detalle.cantidad
            galletas_agrupadas[clave]['subtotal'] += detalle.cantidad * precio_unitario
        
        # Convertir el diccionario a una lista
        detalles_agrupados = list(galletas_agrupadas.values())

        return render_template(
            "ventas/detalle_ventas.html",
            active_page="ventas",
            venta=venta,
            detalles=detalles_agrupados
        )

@venta_bp.route('/obtener_galletas/<int:tipo_venta_id>')
@login_required
@role_required("ADMS", "CAJA") 
def obtener_galletas(tipo_venta_id):
    galletas = (db.session.query(Galleta)
            .filter(Galleta.tipo_galleta_id == tipo_venta_id)
            .all())

    galletas_json = [{"id": g.id_galleta, "nombre": f"{g.galleta} - {g.tipo.nombre}"} for g in galletas]
    
    return jsonify(galletas_json)

@venta_bp.route('/generar_ticket/<int:venta_id>')
@login_required
@role_required("ADMS", "CAJA") 
def generar_ticket(venta_id):
    try:
        # información de la venta
        venta = Venta.query.get_or_404(venta_id)
        detalles = DetalleVentaGalletas.query.filter_by(venta_id=venta_id).all()

        # Diccionario para agrupar items por galleta
        items_agrupados = {}

        # Procesar detalles y agrupar por galleta
        for detalle in detalles:
            lote = LoteGalletas.query.get(detalle.lote_id)
            if not lote:
                continue
                
            galleta = Galleta.query.get(lote.galleta_id)
            if not galleta:
                continue

            precio_unitario = detalle.subtotal / detalle.cantidad
            
            # Si la galleta ya está en el diccionario, sumamos cantidades y subtotales
            if galleta.id_galleta in items_agrupados:
                items_agrupados[galleta.id_galleta]['cantidad'] += detalle.cantidad
                items_agrupados[galleta.id_galleta]['subtotal'] += detalle.subtotal
            else:
                items_agrupados[galleta.id_galleta] = {
                    'nombre': galleta.galleta,
                    'cantidad': detalle.cantidad,
                    'precio': precio_unitario,
                    'subtotal': detalle.subtotal
                }

        # diccionario a lista
        items = list(items_agrupados.values())

        total = venta.total
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        # recargar HTML del ticket
        html = render_template(
            'ventas/ticket.html',
            fecha=fecha_actual,
            hora=hora_actual,
            items=items,
            total=total,
            ticket_num=venta.ticket
        )

        # Opciones PDF
        options = {
            'page-size': 'A7',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': ''
        }

        ruta_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=ruta_wkhtmltopdf)

        # Generar el PDF en memoria
        pdf_bytes = pdfkit.from_string(html, False, options=options, configuration=config)

        # Convertir PDF a Base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Guardar en la base de datos
        venta.ticket = pdf_base64
        db.session.commit()

        return redirect(url_for('venta.ventas'))

    except Exception as e:
        return f"Error al generar ticket: {str(e)}", 500

@venta_bp.route('/obtener_ticket/<int:venta_id>', methods=['GET'])
@login_required
@role_required("ADMS", "CAJA") 
def obtener_ticket(venta_id):
    try:
        venta = Venta.query.filter(Venta.id_venta == venta_id).first()

        if not venta.ticket:
            return jsonify({"error": "No se encontró el ticket en la base de datos"}), 404

        print(jsonify({"ticket_base64": venta.ticket}))
        return jsonify({"ticket_base64": venta.ticket})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@venta_bp.route('/cancelar_venta', methods=['POST'])
@login_required
@role_required("ADMS", "CAJA") 
def cancelar_venta():
    if "detalle_venta" in session:
        # Eliminar toda la lista de detalle_venta
        session["detalle_venta"] = []
        session.modified = True
        print("Venta cancelada: todos los detalles han sido eliminados")
    
    flash("Venta cancelada correctamente", "success")
    return redirect(url_for('venta.registrar_venta'))

@venta_bp.route('/eliminar_detalle/<int:session_id>', methods=['POST'])
@login_required
@role_required("ADMS", "CAJA") 
def eliminar_detalle(session_id):
    if "detalle_venta" in session:
        if 0 <= session_id < len(session["detalle_venta"]):  # Verificar si el índice es válido
            del session["detalle_venta"][session_id]  # Eliminar el elemento
            session.modified = True  # Marcar la sesión como modificada
    
    return redirect(url_for('venta.registrar_venta'))

@venta_bp.route('/corte-caja', methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "CAJA") 
def corte_caja():
    form = CorteCajaForm(request.form)
    cortes = CorteCaja.query.all()
    
    if request.method == 'POST' and form.validate():
        # Verificar si ya existe un corte de caja para la fecha seleccionada
        fecha_corte = form.fecha.data
        corte_existente = CorteCaja.query.filter_by(fecha=fecha_corte).first()
        
        if corte_existente:
            flash("Ya se ha realizado un corte de caja para esta fecha.", "danger")
            return redirect(url_for('venta.corte_caja'))
        
        # Calcular el total de ventas para la fecha
        total_venta = db.session.query(db.func.sum(Venta.total)).filter(Venta.fecha == fecha_corte).scalar()
        
        # Si no hay ventas en esa fecha
        if total_venta is None:
            flash("No hay ventas registradas para esta fecha.", "danger")
            return redirect(url_for('venta.corte_caja'))
        
        # nuevo registro de corte de caja
        nuevo_corte = CorteCaja(
            fecha=fecha_corte,
            totalVenta=total_venta,
            cantidadCaja=form.cantidadCaja.data,
            diferencial=total_venta-form.cantidadCaja.data,
            observaciones=form.observaciones.data
        )
        
        # Agregar y confirmar el nuevo corte de caja en la base de datos
        db.session.add(nuevo_corte)
        db.session.commit()
        
        flash("Corte de caja registrado correctamente.", "success")
        return redirect(url_for('venta.corte_caja'))

    return render_template("ventas/corte_caja.html", form=form, active_page="ventas", cortes=cortes)

@venta_bp.route('/cobrar-pedido', methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "CAJA") 
def pedido_portal():
    pedidos = (
    db.session.query(
        Orden.id_orden,
        Orden.detalles,
        Orden.total,
        Orden.fechaAlta,
        Orden.fechaEntrega,
        Orden.tipoVenta,
        Cliente.idCliente,
        Persona.nombre.label('nombre_cliente'),
        Persona.apPaterno.label('apellido_cliente'),
        DetalleVentaOrden.id_detalleVentaOrden,
        DetalleVentaOrden.cantidad,
        DetalleVentaOrden.subtotal,
        Galleta.galleta.label('nombre_galleta'),
        SolicitudProduccion.idSolicitud,
        SolicitudProduccion.fechaCaducidad,
        SolicitudProduccion.estatus.label('estatus_solicitud')
    )
    .join(Cliente, Cliente.idCliente == Orden.cliente_id)
    .join(Persona, Persona.idPersona == Cliente.idPersona)
    .join(Usuario, Usuario.idUsuario == Cliente.idUsuario)
    .join(DetalleVentaOrden, DetalleVentaOrden.orden_id == Orden.id_orden)
    .join(Galleta, Galleta.id_galleta == DetalleVentaOrden.galletas_id)
    .join(SolicitudProduccion, SolicitudProduccion.detalleorden_id == DetalleVentaOrden.id_detalleVentaOrden)
    .filter(SolicitudProduccion.estatus == 1)
    .all()
    )

    return render_template("ventas/pedidos_portal.html", active_page="ventas", pedidos=pedidos)

@login_required
@role_required("ADMS", "CAJA") 
def registrar_venta(id_orden, total, tipo_venta, detalles):
    try:
        # Crear la venta primero con un ticket temporal
        nueva_venta = Venta(
            total=total,
            fecha=datetime.today().date(),
            hora=datetime.today().time(),
            ticket=f"Ticket-Temp-{id_orden}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            tipoVenta=tipo_venta
        )
        db.session.add(nueva_venta)
        db.session.flush()  # obtener el id_venta generado

        # detalles de la venta sin validar lotes
        items = []
        for detalle in detalles:
            #detalle de venta sin verificar existencias
            nuevo_detalle = DetalleVentaGalletas(
                venta_id=nueva_venta.id_venta,
                lote_id=detalle['lote_id'],
                cantidad=detalle['cantidad'],
                subtotal=detalle['subtotal']
            )
            db.session.add(nuevo_detalle)
            
            # información para el ticket
            galleta = db.session.query(Galleta).get(detalle['galleta_id'])
            precio_unitario = detalle['subtotal'] / detalle['cantidad']
            items.append({
                'nombre': galleta.galleta if galleta else detalle['nombre_galleta'],
                'cantidad': detalle['cantidad'],
                'precio': precio_unitario,
                'subtotal': detalle['subtotal']
            })
        
        # el ticket en base64
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M:%S")
        
        # cargar HTML del ticket
        html = render_template(
            'ventas/ticket.html',
            fecha=fecha_actual,
            hora=hora_actual,
            items=items,
            total=total,
            ticket_num=f"Venta-{nueva_venta.id_venta}"
        )
        
        # Opciones para PDF
        options = {
            'page-size': 'A7',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': ''
        }
        
        ruta_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=ruta_wkhtmltopdf)
        
        # PDF en memoria
        pdf_bytes = pdfkit.from_string(html, False, options=options, configuration=config)
        
        # PDF a Base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Actualizar el ticket en la venta con el PDF en base64
        nueva_venta.ticket = pdf_base64
        
        db.session.commit()
        flash("Venta registrada exitosamente.", "success")
        return nueva_venta.id_venta  # Devolver el ID de la venta para poder redirigir
    
    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar la venta: {str(e)}", "danger")
        return None

@venta_bp.route('/cobrar/<int:id_orden>', methods=['POST'])
@login_required
@role_required("ADMS", "CAJA") 
def cobrar_pedido(id_orden):
    pedido = db.session.query(Orden).filter_by(id_orden=id_orden).first()
    if not pedido:
        flash("Orden no encontrada", "danger")
        return redirect(url_for('venta.pedido_portal'))

    try:
        # detalles del pedido
        detalles = (db.session.query(DetalleVentaOrden, Galleta)
                    .join(Galleta, Galleta.id_galleta == DetalleVentaOrden.galletas_id)
                    .filter(DetalleVentaOrden.orden_id == id_orden)
                    .all())

        # registro de venta
        ahora = datetime.now()
        nueva_venta = Venta(
            total=pedido.total,
            fecha=ahora.date(),
            hora=ahora.time(),
            ticket=f"TK-{ahora.strftime('%Y%m%d%H%M%S')}",
            tipoVenta=pedido.tipoVenta
        )
        db.session.add(nueva_venta)
        db.session.flush()  # Para obtener el ID de la venta

        # Diccionario para acumular cantidades por galleta
        galletas_vendidas = {}

        # cada detalle del pedido
        for d, galleta in detalles:
            # Acumular cantidad para actualizar existencia en Galleta
            galletas_vendidas[galleta.id_galleta] = galletas_vendidas.get(galleta.id_galleta, 0) + d.cantidad

            # lotes disponibles ordenados por fecha (más antiguos primero)
            lotes_disponibles = (db.session.query(LoteGalletas)
                                .filter(LoteGalletas.galleta_id == galleta.id_galleta)
                                .filter(LoteGalletas.existencia > 0)
                                .order_by(LoteGalletas.fechaCaducidad.asc())
                                .all())

            if not lotes_disponibles:
                raise Exception(f"No hay lotes disponibles para {galleta.galleta}")

            # Asignar cantidades a lotes
            cantidad_restante = d.cantidad

            for lote in lotes_disponibles:
                if cantidad_restante <= 0:
                    break

                cantidad_a_usar = min(cantidad_restante, lote.existencia)

                # Registrar detalle de venta por lote
                detalle_venta = DetalleVentaGalletas(
                    venta_id=nueva_venta.id_venta,
                    lote_id=lote.id_lote,
                    cantidad=cantidad_a_usar,
                    subtotal=cantidad_a_usar * (d.subtotal / d.cantidad)  # Mantener proporción del subtotal
                )
                db.session.add(detalle_venta)

                # Actualizar existencia del lote
                lote.existencia -= cantidad_a_usar
                if lote.existencia < 0:
                    raise Exception(f"Existencia negativa en lote {lote.id_lote}")

                cantidad_restante -= cantidad_a_usar

            if cantidad_restante > 0:
                raise Exception(f"No hay suficiente existencia para {galleta.galleta}")

        # Actualizar existencias de Galleta
        for galleta_id, cantidad in galletas_vendidas.items():
            galleta = db.session.query(Galleta).get(galleta_id)
            if galleta:
                galleta.existencia -= cantidad
                if galleta.existencia < 0:
                    raise Exception(f"Existencia negativa para {galleta.galleta}")

        # Actualizar estado de las solicitudes de producción
        solicitudes = (db.session.query(SolicitudProduccion)
                      .join(DetalleVentaOrden, DetalleVentaOrden.id_detalleVentaOrden == SolicitudProduccion.detalleorden_id)
                      .filter(DetalleVentaOrden.orden_id == id_orden)
                      .all())

        for solicitud in solicitudes:
            solicitud.estatus = 2  # Estado "Vendido" o "Entregado"

        # Confirmar cambios
        db.session.commit()
        crear_ticket_pdf(nueva_venta.id_venta)
        flash("Pedido cobrado exitosamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al cobrar pedido: {str(e)}", "danger")

    return redirect(url_for('venta.ventas'))

def crear_ticket_pdf(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    detalles = DetalleVentaGalletas.query.filter_by(venta_id=venta_id).all()

    items_agrupados = {}

    for detalle in detalles:
        lote = LoteGalletas.query.get(detalle.lote_id)
        if not lote:
            continue

        galleta = Galleta.query.get(lote.galleta_id)
        if not galleta:
            continue

        precio_unitario = detalle.subtotal / detalle.cantidad

        if galleta.id_galleta in items_agrupados:
            items_agrupados[galleta.id_galleta]['cantidad'] += detalle.cantidad
            items_agrupados[galleta.id_galleta]['subtotal'] += detalle.subtotal
        else:
            items_agrupados[galleta.id_galleta] = {
                'nombre': galleta.galleta,
                'cantidad': detalle.cantidad,
                'precio': precio_unitario,
                'subtotal': detalle.subtotal
            }

    items = list(items_agrupados.values())
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    hora_actual = datetime.now().strftime("%H:%M:%S")

    html = render_template(
        'ventas/ticket.html',
        fecha=fecha_actual,
        hora=hora_actual,
        items=items,
        total=venta.total,
        ticket_num=venta.ticket
    )

    options = {
        'page-size': 'A7',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': ''
    }

    ruta_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=ruta_wkhtmltopdf)
    pdf_bytes = pdfkit.from_string(html, False, options=options, configuration=config)
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    venta.ticket = pdf_base64
    db.session.commit()

@venta_bp.route("/detalles_pedidos", methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "CAJA") 
def detalles_pedido():
    if request.method == 'GET':
        orden_id = request.args.get('idOrden')

        # Consulta principal para obtener la orden
        orden = db.session.query(Orden).filter(Orden.id_orden == orden_id).first()

        if not orden:
            flash("Orden no encontrada", "error")
            return redirect(url_for("venta.pedido_portal"))

        # Consulta para obtener los detalles con información relacionada
        detalles_query = db.session.query(
            DetalleVentaOrden.galletas_id,
            Galleta.galleta.label("nombre_galleta"),
            DetalleVentaOrden.cantidad,
            TipoGalleta.nombre.label("tipo_galleta"),
            TipoGalleta.costo.label("precio_unitario"),
            DetalleVentaOrden.subtotal.label("subtotal")
        ).join(
            Galleta, DetalleVentaOrden.galletas_id == Galleta.id_galleta
        ).join(
            TipoGalleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta
        ).filter(
            DetalleVentaOrden.orden_id == orden_id
        ).all()

        # Agrupar los detalles por id_galleta
        galletas_agrupadas = {}
        for galleta_id, nombre_galleta, cantidad, tipo_galleta, precio_unitario, subtotal in detalles_query:
            # Crear una clave para la galleta
            clave = galleta_id
            
            if clave not in galletas_agrupadas:
                galletas_agrupadas[clave] = {
                    'id_galleta': galleta_id,
                    'nombre_galleta': nombre_galleta,
                    'tipo_galleta': tipo_galleta,
                    'precio_unitario': precio_unitario,
                    'cantidad': 0,
                    'subtotal': 0
                }
            
            # Sumar cantidad y subtotal
            galletas_agrupadas[clave]['cantidad'] += cantidad
            galletas_agrupadas[clave]['subtotal'] += subtotal
        
        # diccionario a una lista
        detalles_agrupados = list(galletas_agrupadas.values())

        return render_template(
            "ventas/detalle_pedidos.html",
            active_page="ventas",
            orden=orden,
            detalles=detalles_agrupados
        )

@venta_bp.route('/merma_galletas', methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "CAJA") 
def merma_galletas():
    form = MermaGalletasForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            # datos del formulario
            lote_id = int(request.form.get('lote_merma'))
            cantidad = form.cantidad.data
            tipo_merma = form.tipo_merma.data
            fecha = form.fecha.data or date.today()
            descripcion = form.descripcion.data

            # el lote correspondiente
            lote = LoteGalletas.query.get(lote_id)
            if not lote:
                flash('Lote no encontrado.', 'danger')
                return redirect(url_for('venta.merma_galletas'))

            # Validar que haya suficiente existencia en el lote
            if cantidad > lote.existencia:
                flash('No hay suficiente existencia en el lote seleccionado.', 'danger')
                return redirect(url_for('venta.merma_galletas'))

            #nueva merma
            nueva_merma = MermaGalleta(
                lote_id=lote_id,
                cantidad=cantidad,
                tipo_merma=tipo_merma,
                fecha=fecha,
                descripcion=descripcion
            )

            # Descontar la cantidad de la merma del lote
            lote.existencia -= cantidad

            # Guardar los cambios
            db.session.add(nueva_merma)
            db.session.commit()

            flash('Merma registrada y existencia actualizada correctamente.', 'success')
            return redirect(url_for('venta.merma_galletas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la merma: {str(e)}', 'danger')

    return render_template("ventas/registrar_merma.html", active_page="ventas", form=form)

@venta_bp.route('/obtener_reservas')
@login_required
def obtener_reservas():
    if 'detalle_venta' not in session:
        return jsonify([])
    
    # Procesar reservas para todas las galletas
    reservas = []
    for item in session['detalle_venta']:
        for lote in item.get('lotes', []):
            reservas.append({
                'id_galleta': item['id_galleta'],
                'lote_id': lote['lote_id'],
                'cantidad': lote['cantidad']
            })
    
    return jsonify(reservas)

@venta_bp.route('/obtener_lotes/<int:galleta_id>')
@login_required
@role_required("ADMS", "CAJA") 
def obtener_lotes(galleta_id):

    # Asegurarse que existe la variable de sesión
    if 'detalle_venta' not in session:
        session['detalle_venta'] = []
    
    # todos los lotes válidos para esta galleta
    lotes = (db.session.query(LoteGalletas)
            .options(db.joinedload(LoteGalletas.galleta))
            .filter(LoteGalletas.galleta_id == galleta_id)
            .filter(LoteGalletas.existencia > 0)
            .all()
            )
    
    # todas las reservas actuales para esta galleta
    reservas = []
    for item in session['detalle_venta']:
        if item.get('id_galleta') == galleta_id:
            for lote in item.get('lotes', []):
                reservas.append({
                    'lote_id': lote['lote_id'],
                    'cantidad': lote['cantidad']
                })
    
    lotes_json = []
    for lote in lotes:
        # Calcular reservas para este lote específico sumando todas las reservas que coincidan con este lote
        reservado = sum(r["cantidad"] for r in reservas if r["lote_id"] == lote.id_lote)
        
        existencia_disponible = lote.existencia - reservado
        
        # Solo incluir lotes con existencia disponible
        if existencia_disponible > 0:
            lotes_json.append({
                "id": lote.id_lote,
                "existencia": existencia_disponible,
                "fechaCaducidad": lote.fechaCaducidad.strftime('%Y/%m/%d'),
                "existencia_real": lote.existencia 
            })
    
    return jsonify(lotes_json)

@venta_bp.route('/obtener/lotes', methods=['GET'])
@login_required
@role_required("ADMS", "CAJA") 
def get_lotes():
    try:
        lotes = db.session.query(
            LoteGalletas.id_lote,
            LoteGalletas.fechaProduccion,
            LoteGalletas.fechaCaducidad,
            LoteGalletas.existencia,
            Galleta.galleta.label("nombre_galleta"),
            TipoGalleta.nombre.label("tipo_galleta")
        ).join(Galleta, LoteGalletas.galleta_id == Galleta.id_galleta) \
         .join(TipoGalleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta) \
         .filter(LoteGalletas.existencia > 0) \
         .all()

        lotes_json = [
            {
                "id_lote": lote.id_lote,
                "fechaProduccion": lote.fechaProduccion.strftime('%Y-%m-%d'),
                "fechaCaducidad": lote.fechaCaducidad.strftime('%Y-%m-%d'),
                "existencia": lote.existencia,
                "nombre_galleta": lote.nombre_galleta,
                "tipo_galleta": lote.tipo_galleta
            }
            for lote in lotes
        ]

        return jsonify(lotes_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
