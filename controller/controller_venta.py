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
from model.merma_galletas import MermaGalletas
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
def ventas():
    form = VentaForm(request.form)
    ventas = Venta.query.all()
    
    return render_template("ventas/ventas.html", active_page="ventas", ventas=ventas, form=form)

@venta_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_venta():
    form = VentaForm(request.form)

    if 'detalle_venta' not in session:
        session['detalle_venta'] = []

    if request.method == 'POST' and form.validate():
        tipo_galleta_id = request.form.get('tipo_galleta')
        lote_id = request.form.get('lote')
        existencia_lote = request.form.get('existencia_lote')
        fecha_caducidad_lote = request.form.get('fecha_caducidad_lote')
        cantidad = form.cantidad.data

        try:
            existencia_lote = int(existencia_lote) if existencia_lote else 0
            cantidad = int(cantidad)
            lote_id = int(lote_id)
        except ValueError:
            flash("Error: eligé una galleta y lote.", "danger")
            return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                detalle_venta=session['detalle_venta'])

        # Validar fecha de caducidad
        if fecha_caducidad_lote:
            fecha_caducidad = datetime.strptime(fecha_caducidad_lote, '%Y/%m/%d').date()
            hoy = datetime.now().date()
            if fecha_caducidad < hoy:
                flash("Error: El lote seleccionado está caducado.", "danger")
                return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                    detalle_venta=session['detalle_venta'])

        # Obtenemos el lote actual de la base de datos para tener la cantidad real
        lote_actual = LoteGalletas.query.get(lote_id)
        if not lote_actual:
            flash("Error: El lote seleccionado no existe.", "danger")
            return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                detalle_venta=session['detalle_venta'])
        
        # Calcular las reservas actuales para este lote específico
        reservas_totales = sum(item["cantidad"] for item in session['detalle_venta'] if item["lote_id"] == lote_id)
        
        # Calcular existencia real disponible
        existencia_disponible = lote_actual.existencia - reservas_totales
        
        # Validar que no se venda más de lo disponible
        if cantidad > existencia_disponible:
            flash(f"Error: No hay suficiente existencia disponible en el lote. Existencia actual: {existencia_disponible}", "danger")
            return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                detalle_venta=session['detalle_venta'])

        tipo_galleta = Galleta.query.get(tipo_galleta_id)
        if not tipo_galleta:
            flash("Error: La galleta seleccionada no existe.", "danger")
            return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                                detalle_venta=session['detalle_venta'])

        precio = tipo_galleta.tipo.costo
        subtotal = cantidad * precio

        nueva_venta = {
            "id_galleta": tipo_galleta_id,
            "nombre": tipo_galleta.galleta,
            "tipo": tipo_galleta.tipo.nombre,
            "cantidad": cantidad,
            "precio_unitario": float(precio),
            "subtotal": float(subtotal),
            "lote_id": lote_id
        }

        # Guardar la venta en la sesión
        session['detalle_venta'].append(nueva_venta)
        session.modified = True

        return redirect(url_for('venta.registrar_venta'))

    return render_template('ventas/registrar_ventas.html', form=form, active_page="ventas", 
                        detalle_venta=session['detalle_venta'])

@venta_bp.route('/finalizar', methods=['POST'])
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

        # Generar un ticket único
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
        db.session.flush()  # Para obtener el ID de la venta

        # Registrar detalles y actualizar existencias
        for detalle in session['detalle_venta']:
            # Registrar detalle
            nuevo_detalle = DetalleVentaGalletas(
                venta_id=nueva_venta.id_venta,
                lote_id=detalle['lote_id'],
                cantidad=detalle['cantidad'],
                subtotal=detalle['subtotal']
            )
            db.session.add(nuevo_detalle)

            # Actualizar existencia real
            lote = LoteGalletas.query.get(detalle['lote_id'])
            if lote:
                lote.existencia -= detalle['cantidad']
                if lote.existencia < 0:
                    db.session.rollback()
                    flash(f"Error: Existencia insuficiente en lote {lote.id_lote}. La venta no se completó.", "danger")
                    return redirect(url_for('venta.registrar_venta'))

        db.session.commit()

        # Limpiar la sesión después de una venta exitosa
        venta_id = nueva_venta.id_venta  # Guardar el ID antes de limpiar la sesión
        session.pop('detalle_venta', None)
        session.modified = True

        flash("Venta registrada exitosamente!", "success")
        
        # Redirigir a la generación del ticket
        return redirect(url_for('venta.generar_ticket', venta_id=venta_id))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar la venta: {str(e)}", "danger")
        return redirect(url_for('venta.registrar_venta'))
    
@venta_bp.route("/detalles", methods=['GET', 'POST'])
def detalles_venta():
    if request.method == 'GET':
        id_venta = request.args.get('idVenta')
        
        # Consulta principal para obtener la venta
        venta = db.session.query(Venta).filter(Venta.id_venta == id_venta).first()
        
        # Consulta para obtener los detalles con información relacionada
        detalles = db.session.query(
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

        return render_template(
            "ventas/detalle_ventas.html",
            active_page="ventas",
            venta=venta,
            detalles=detalles
        )

@venta_bp.route('/obtener_galletas/<int:tipo_venta_id>')
def obtener_galletas(tipo_venta_id):
    galletas = (db.session.query(Galleta)
            .filter(Galleta.tipo_galleta_id == tipo_venta_id)
            .all())

    galletas_json = [{"id": g.id_galleta, "nombre": f"{g.galleta} - {g.tipo.nombre}"} for g in galletas]
    
    return jsonify(galletas_json)

@venta_bp.route('/obtener_lotes/<int:galleta_id>')
def obtener_lotes(galleta_id):
    # Asegurarse que existe la variable de sesión
    if 'detalle_venta' not in session:
        session['detalle_venta'] = []
    
    # Obtener todos los lotes válidos para esta galleta
    lotes = (db.session.query(LoteGalletas)
            .options(db.joinedload(LoteGalletas.galleta))
            .filter(LoteGalletas.galleta_id == galleta_id)
            .filter(LoteGalletas.existencia > 0)
            .all()
            )
    
    lotes_json = []
    for lote in lotes:
        # Calcular reservas para este lote específico
        reservas = sum(item["cantidad"] for item in session['detalle_venta'] 
                       if item["lote_id"] == lote.id_lote)
        
        existencia_disponible = lote.existencia - reservas
        
        # Solo incluir lotes con existencia disponible positiva
        if existencia_disponible > 0:
            lotes_json.append({
                "id": lote.id_lote,
                "existencia": existencia_disponible,  # Mostrar la existencia disponible
                "fechaCaducidad": lote.fechaCaducidad.strftime('%Y/%m/%d'),
                "existencia_real": lote.existencia  # Mantener referencia a la existencia real
            })
    
    return jsonify(lotes_json)

@venta_bp.route('/generar_ticket/<int:venta_id>')
def generar_ticket(venta_id):
    try:
        # Obtener la información de la venta
        venta = Venta.query.get_or_404(venta_id)
        detalles = DetalleVentaGalletas.query.filter_by(venta_id=venta_id).all()

        # Preparar los datos para el template
        items = []
        for detalle in detalles:
            lote = LoteGalletas.query.get(detalle.lote_id)
            galleta = Galleta.query.get(lote.galleta_id) if lote else None

            if galleta:
                precio_unitario = detalle.subtotal / detalle.cantidad
                items.append({
                    'nombre': galleta.galleta,
                    'cantidad': detalle.cantidad,
                    'precio': precio_unitario,
                    'subtotal': detalle.subtotal
                })

        total = venta.total
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        # Renderizar HTML del ticket
        html = render_template(
            'ventas/ticket.html',
            fecha=fecha_actual,
            hora=hora_actual,
            items=items,
            total=total,
            ticket_num=venta.ticket
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

        # Generar el PDF en memoria
        pdf_bytes = pdfkit.from_string(html, False, options=options, configuration=config)

        # Convertir PDF a Base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Guardar en la base de datos (suponiendo que `Venta` tiene un campo `ticket_pdf`)
        venta.ticket = pdf_base64
        db.session.commit()

        return redirect(url_for('venta.ventas'))

    except Exception as e:
        return f"Error al generar ticket: {str(e)}", 500

@venta_bp.route('/obtener_ticket/<int:venta_id>', methods=['GET'])
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
def cancelar_venta():
    if "detalle_venta" in session:
        # Eliminar toda la lista de detalle_venta
        session["detalle_venta"] = []
        session.modified = True
        print("Venta cancelada: todos los detalles han sido eliminados")
    
    flash("Venta cancelada correctamente", "success")
    return redirect(url_for('venta.registrar_venta'))

@venta_bp.route('/eliminar_detalle/<int:session_id>', methods=['POST'])
def eliminar_detalle(session_id):
    if "detalle_venta" in session:
        if 0 <= session_id < len(session["detalle_venta"]):  # Verificar si el índice es válido
            del session["detalle_venta"][session_id]  # Eliminar el elemento
            session.modified = True  # Marcar la sesión como modificada
    
    return redirect(url_for('venta.registrar_venta'))

@venta_bp.route('/corte-caja', methods=['GET', 'POST'])
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
        
        # Calcular el total de ventas para la fecha seleccionada
        total_venta = db.session.query(db.func.sum(Venta.total)).filter(Venta.fecha == fecha_corte).scalar()
        
        # Si no hay ventas en esa fecha, mostrar mensaje de error
        if total_venta is None:
            flash("No hay ventas registradas para esta fecha.", "danger")
            return redirect(url_for('venta.corte_caja'))
        
        # Crear el nuevo registro de corte de caja
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
def pedido_portal():
    pedidos = (
    db.session.query(
        Orden.id_orden,
        Orden.descripcion,
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
        db.session.flush()  # Para obtener el id_venta generado

        # Registrar los detalles de la venta sin validar lotes
        items = []
        for detalle in detalles:
            # Crear el detalle de venta sin verificar existencias
            nuevo_detalle = DetalleVentaGalletas(
                venta_id=nueva_venta.id_venta,
                lote_id=detalle['lote_id'],
                cantidad=detalle['cantidad'],
                subtotal=detalle['subtotal']
            )
            db.session.add(nuevo_detalle)
            
            # Agregar información para el ticket
            galleta = db.session.query(Galleta).get(detalle['galleta_id'])
            precio_unitario = detalle['subtotal'] / detalle['cantidad']
            items.append({
                'nombre': galleta.galleta if galleta else detalle['nombre_galleta'],
                'cantidad': detalle['cantidad'],
                'precio': precio_unitario,
                'subtotal': detalle['subtotal']
            })
        
        # Ahora generar el ticket en base64
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M:%S")
        
        # Renderizar HTML del ticket
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
        
        # Generar el PDF en memoria
        pdf_bytes = pdfkit.from_string(html, False, options=options, configuration=config)
        
        # Convertir PDF a Base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Actualizar el ticket en la venta con el PDF en base64
        nueva_venta.ticket = pdf_base64
        
        db.session.commit()
        flash("Venta registrada exitosamente.", "success")
        return nueva_venta.id_venta  # Devolver el ID de la venta para poder redirigir si es necesario
    
    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar la venta: {str(e)}", "danger")
        return None

@venta_bp.route('/cobrar/<int:id_orden>', methods=['POST'])
def cobrar_pedido(id_orden):
    pedido = db.session.query(Orden).filter_by(id_orden=id_orden).first()
    if not pedido:
        flash("Orden no encontrada", "danger")
        return redirect(url_for('venta.pedido_portal'))
    
    detalles = (db.session.query(DetalleVentaOrden, Galleta)
                .join(Galleta, Galleta.id_galleta == DetalleVentaOrden.galletas_id)
                .filter(DetalleVentaOrden.orden_id == id_orden)
                .all())
    
    detalle_data = []
    for d, galleta in detalles:
        # Buscar un lote para esta galleta según su ID y tipo
        lote = (db.session.query(LoteGalletas)
            .join(Galleta, Galleta.id_galleta == LoteGalletas.galleta_id)
            .filter(
                LoteGalletas.galleta_id == galleta.id_galleta,
                Galleta.tipo_galleta_id == galleta.tipo_galleta_id  # Asumiendo que la tabla Galleta tiene un campo tipo_id
            )
            .first())
        lote_id = lote.id_lote if lote else 1  # Valor predeterminado si no hay lote
        
        detalle_data.append({
            'lote_id': lote_id,
            'galleta_id': d.galletas_id,
            'nombre_galleta': galleta.galleta,
            'cantidad': d.cantidad,
            'subtotal': d.subtotal
        })
    
    venta_id = registrar_venta(id_orden, pedido.total, pedido.tipoVenta, detalle_data)
    
    if venta_id:
        # Actualizar el estado de las solicitudes de producción
        solicitudes = (db.session.query(SolicitudProduccion)
                      .join(DetalleVentaOrden, DetalleVentaOrden.id_detalleVentaOrden == SolicitudProduccion.detalleorden_id)
                      .filter(DetalleVentaOrden.orden_id == id_orden)
                      .all())
        
        for solicitud in solicitudes:
            solicitud.estatus = 2  # Suponiendo que 2 es el estado de "Vendido" o "Entregado"
        
        db.session.commit()
        flash("Pedido cobrado exitosamente", "success")
    
    return redirect(url_for('venta.ventas'))

@venta_bp.route("/detalles_pedidos", methods=['GET', 'POST'])
def detalles_pedido():
    if request.method == 'GET':
        orden_id = request.args.get('idOrden')

        # Consulta principal para obtener la orden
        orden = db.session.query(Orden).filter(Orden.id_orden == orden_id).first()

        if not orden:
            flash("Orden no encontrada", "error")
            return redirect(url_for("venta.pedido_portal"))

        # Consulta para obtener los detalles con información relacionada
        detalles = db.session.query(
            DetalleVentaOrden.id_detalleVentaOrden,
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

        return render_template(
            "ventas/detalle_pedidos.html",
            active_page="ventas",
            orden=orden,
            detalles=detalles
        )

@venta_bp.route('/merma_galletas', methods=['GET', 'POST'])
def merma_galletas():
    form = MermaGalletasForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            # Obtener datos del formulario
            lote_id = int(request.form.get('lote_merma'))
            cantidad = form.cantidad.data
            tipo_merma = form.tipo_merma.data
            fecha = form.fecha.data or date.today()
            descripcion = form.descripcion.data

            # Obtener el lote correspondiente
            lote = LoteGalletas.query.get(lote_id)
            if not lote:
                flash('Lote no encontrado.', 'danger')
                return redirect(url_for('venta.merma_galletas'))

            # Validar que haya suficiente existencia en el lote
            if cantidad > lote.existencia:
                flash('No hay suficiente existencia en el lote seleccionado.', 'danger')
                return redirect(url_for('venta.merma_galletas'))

            # Crear la nueva merma
            nueva_merma = MermaGalletas(
                lote_id=lote_id,
                cantidad=cantidad,
                tipo_merma=tipo_merma,
                fecha=fecha,
                descripcion=descripcion
            )

            # Descontar la cantidad de la merma del lote
            lote.existencia -= cantidad

            # Guardar los cambios en la base de datos
            db.session.add(nueva_merma)
            db.session.commit()

            flash('Merma registrada y existencia actualizada correctamente.', 'success')
            return redirect(url_for('venta.merma_galletas'))  # Redirigir a la misma página o a otra

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la merma: {str(e)}', 'danger')

    return render_template("ventas/registrar_merma.html", active_page="ventas", form=form)

@venta_bp.route('/obtener/lotes', methods=['GET'])
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
