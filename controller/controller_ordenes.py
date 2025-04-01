
import ast
import traceback
from flask import (
    Blueprint,
    Flask,
    json,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from extensions import db
from model.insumo import Insumos
from model.lote_insumo import LoteInsumo
from model.lote_galleta import LoteGalleta
from model.merma_insumo import MermasInsumos
from model.receta import Receta
from model.tipo_galleta import TipoGalleta
from model.galleta import Galleta
from model.detalle_Orden import DetalleVentaOrden
from model.orden import Orden
from model.solicitud import SolicitudProduccion
from forms.ordenMerma_form import MermaForm 
from decimal import Decimal

# Crear el Blueprint para orden
orden_bp = Blueprint("orden", __name__, url_prefix="/orden")

def estado_a_texto(estado):
    return {
        0: 'INACTIVO',
        1: 'TERMINADO',
        2: 'ENTREGADO',
        3: 'LOTE'
    }.get(estado, 'DESCONOCIDO')

def obtener_detalle_orden(id_detalle):
    """Obtiene el detalle completo de la orden"""
    return db.session.query(
        DetalleVentaOrden,
        Galleta,
        Receta,
        Orden,
        TipoGalleta  # Añadimos TipoGalleta a la consulta
    ).join(
        Galleta, DetalleVentaOrden.galletas_id == Galleta.id_galleta
    ).join(
        Receta, Galleta.receta_id == Receta.idReceta
    ).join(
        Orden, DetalleVentaOrden.orden_id == Orden.id_orden
    ).join(
        TipoGalleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta  # Unimos con TipoGalleta
    ).filter(
        DetalleVentaOrden.id_detalleVentaOrden == id_detalle
    ).first()

def parsear_ingredientes(ingredientes_raw):
    """Convierte los ingredientes a una lista válida"""
    if isinstance(ingredientes_raw, str):
        try:
            return json.loads(ingredientes_raw)
        except json.JSONDecodeError:
            try:
                return json.loads(ingredientes_raw.replace("'", '"'))
            except:
                try:
                    return eval(ingredientes_raw)
                except:
                    raise ValueError("Error al parsear ingredientes")
    elif isinstance(ingredientes_raw, list):
        return ingredientes_raw
    raise ValueError("Formato de ingredientes no válido")

def calcular_cantidad_ingrediente(cantidad_original, factor, unidad):
    """Calcula la cantidad necesaria con el redondeo apropiado"""
    cantidad_calculada = cantidad_original * factor
    unidad = unidad.lower().strip()
    
    if unidad == 'unidad':
        if cantidad_calculada <= 0:
            cantidad_final = 0
        elif cantidad_calculada < 1:
            cantidad_final = 1  # Mínimo 1 unidad
        else:
            cantidad_final = round(cantidad_calculada)
        return int(cantidad_final), abs(cantidad_final - cantidad_calculada) > 0.1
    else:
        return round(cantidad_calculada, 2), False

def procesar_ingredientes(receta, cantidad_galletas, cantidad_pedido, presentacion=None):
    """Procesa ingredientes con conversión CORRECTA de cajas a galletas"""
    print(f"\n=== INICIANDO PROCESAR INGREDIENTES ===")
    print(f"Presentación recibida: {presentacion}")
    print(f"Cantidad pedido original: {cantidad_pedido}")
    
    ingredientes = []
    try:
        if not receta.ingredientes:
            return ingredientes

        # CONVERSIÓN DEFINITIVA A GALLETAS (CORRECCIÓN CLAVE)
        presentacion = presentacion.lower() if presentacion else None
        if presentacion == 'caja de kilo':
            total_galletas = int(cantidad_pedido * 27)  # 27 galletas por caja
            print(f"Conversión: {cantidad_pedido} cajas de kilo = {total_galletas} galletas")
        elif presentacion == 'caja de 700':
            total_galletas = int(cantidad_pedido * 19)  # 19 galletas por caja
            print(f"Conversión: {cantidad_pedido} cajas de 700 = {total_galletas} galletas")
        else:
            total_galletas = int(cantidad_pedido)  # Unidades individuales
            print(f"Unidades: {total_galletas} galletas")

        # Calcular factor basado en la receta
        cantidad_base = receta.cantidad_galletas if receta.cantidad_galletas else 100
        factor = total_galletas / cantidad_base
        print(f"Factor de cálculo: {factor} ({total_galletas}/{cantidad_base})")

        # Procesar cada ingrediente
        ingredientes_raw = parsear_ingredientes(receta.ingredientes)
        for ingrediente in ingredientes_raw:
            try:
                cantidad_original = float(ingrediente['cantidad'])
                cantidad_final, ajustado = calcular_cantidad_ingrediente(
                    cantidad_original,
                    factor,
                    ingrediente.get('unidad', '')
                )
                print(f"  - {ingrediente['insumo']}: {cantidad_original} -> {cantidad_final}")

                ingrediente.update({
                    'cantidad_necesaria': cantidad_final,
                    'total_galletas': total_galletas,
                    'presentacion': presentacion,
                    'cantidad_cajas': cantidad_pedido if presentacion in ['caja de kilo', 'caja de 700'] else None
                })
                
            except (ValueError, KeyError) as e:
                print(f"¡Error procesando {ingrediente.get('insumo')}! {str(e)}")
                ingrediente['cantidad_necesaria'] = 'N/A'

            ingredientes.append(ingrediente)

    except Exception as e:
        print(f"¡ERROR GRAVE en procesar_ingredientes! {str(e)}")
        raise

    print("=== FIN DE PROCESAR INGREDIENTES ===\n")
    return ingredientes

def obtener_presentacion_galleta(id_galleta):
    """Obtiene el tipo de presentación de una galleta"""
    return db.session.query(
        TipoGalleta.nombre
    ).join(
        Galleta, TipoGalleta.id_tipo_galleta == Galleta.tipo_galleta_id
    ).filter(
        Galleta.id_galleta == id_galleta
    ).scalar()

def verificar_actualizar_estatus_orden(id_orden):
    """Verifica si la fecha de entrega ha pasado y actualiza el estatus a 3 (LOTE) si es necesario"""
    try:
        # Obtener la orden con su fecha de entrega
        orden = Orden.query.get(id_orden)
        if not orden:
            print(f"Orden {id_orden} no encontrada")
            return False
        
        hoy = datetime.now().date()
        fecha_entrega = orden.fechaEntrega.date()
        
        # Verificar si la fecha de entrega ha pasado
        if fecha_entrega < hoy:
            print(f"La orden {id_orden} ha pasado su fecha de entrega ({fecha_entrega})")
            
            # Actualizar todas las solicitudes relacionadas con esta orden
            solicitudes = db.session.query(
                SolicitudProduccion
            ).join(
                DetalleVentaOrden,
                SolicitudProduccion.detalleorden_id == DetalleVentaOrden.id_detalleVentaOrden
            ).filter(
                DetalleVentaOrden.orden_id == id_orden,
                SolicitudProduccion.estatus.in_([0, 1])  # Solo INACTIVO o TERMINADO
            ).all()
            
            for solicitud in solicitudes:
                # Obtener el detalle completo de la orden
                detalle_completo = obtener_detalle_orden(solicitud.detalleorden_id)
                if not detalle_completo:
                    continue
                
                detalle_orden, galleta, receta, orden, tipo_galleta = detalle_completo
                
                solicitud.estatus = 3  # LOTE
                db.session.add(solicitud)
                print(f"Actualizada solicitud {solicitud.idSolicitud} a LOTE")

                # Calcular la cantidad total de galletas usando la presentación del tipo de galleta
                presentacion = tipo_galleta.nombre if tipo_galleta else None
                cantidad_total = calcular_cantidad_total_galletas(
                    detalle_orden.cantidad,
                    presentacion
                )
                
                # Insertar en lote_galletas
                insertar_lote_galleta(
                    galleta.id_galleta,
                    cantidad_total,
                    solicitud.fechaCaducidad
                )
            
            db.session.commit()
            return True
        
        return False
    
    except Exception as e:
        print(f"Error al verificar estatus de orden {id_orden}: {str(e)}")
        traceback.print_exc()
        db.session.rollback()
        return False


def calcular_cantidad_total_galletas(cantidad_pedido, presentacion):
    """Calcula la cantidad total de galletas según la presentación"""
    if presentacion.lower() == 'caja de kilo':
        return int(cantidad_pedido * 27)  # 27 galletas por caja
    elif presentacion.lower() == 'caja de 700':
        return int(cantidad_pedido * 19)  # 19 galletas por caja
    else:
        return int(cantidad_pedido)  # Unidades individuales

def insertar_lote_galleta(galleta_id, cantidad, fecha_caducidad):
    """Inserta un nuevo registro en la tabla lotesGalletas"""
    try:
        # Calcular fecha de producción (7 días antes de la caducidad)
        fecha_produccion = fecha_caducidad - timedelta(days=7)
        
        # Crear el nuevo lote
        nuevo_lote = LoteGalleta(
            galleta_id=galleta_id,
            cantidad=cantidad,
            costo=200.00,  # Costo fijo de producción
            existencia=cantidad,  # Misma cantidad que se produjo
            fechaProduccion=fecha_produccion,
            fechaCaducidad=fecha_caducidad
        )
        
        db.session.add(nuevo_lote)
        db.session.commit()
        print(f"Nuevo lote creado: {nuevo_lote.id_lote}")
        return True
    except Exception as e:
        print(f"Error al insertar lote de galletas: {str(e)}")
        db.session.rollback()
        return False


#ruta principal donde muestra los pedidos y llama las funciones anteirores para las fechas y los estatus y agregar a lotes
@orden_bp.route("/")
def ordenes():
    try:
        #fecha actual
        hoy = datetime.now().date()
        
        resultados = db.session.query(
            DetalleVentaOrden.id_detalleVentaOrden.label('id_detalle'),
            Galleta.galleta,
            Orden.fechaEntrega,
            SolicitudProduccion.estatus,
            DetalleVentaOrden.cantidad,
            Orden.id_orden
        ).join(
            Galleta, DetalleVentaOrden.galletas_id == Galleta.id_galleta
        ).join(
            Orden, DetalleVentaOrden.orden_id == Orden.id_orden
        ).outerjoin(
            SolicitudProduccion,
            DetalleVentaOrden.id_detalleVentaOrden == SolicitudProduccion.detalleorden_id
        ).filter(
            (SolicitudProduccion.estatus.in_([0, 1])) | 
            (SolicitudProduccion.estatus == None)
        ).order_by(
            Orden.fechaEntrega.asc()
        ).all()

        # Verificamos ordenes vencidas
        ordenes_procesadas = set()
        
        for _, _, _, _, _, id_orden in resultados:
            if id_orden not in ordenes_procesadas:
                verificar_actualizar_estatus_orden(id_orden)
                ordenes_procesadas.add(id_orden)

        ordenes_a_actualizar = []
        datos_ordenes = []
        
        for id_detalle, nombre_galleta, fecha_entrega, estatus, cantidad, _ in resultados:
            estado_actual = estatus if estatus is not None else 0
            fecha_entrega_date = fecha_entrega.date()

            if estado_actual == 1 and fecha_entrega_date < hoy:
                ordenes_a_actualizar.append(id_detalle)

            datos_ordenes.append({
                "id_detalle": id_detalle,
                "galleta": nombre_galleta,
                "fecha": fecha_entrega.strftime('%d/%m/%Y %H:%M'),
                "estado": estado_a_texto(estado_actual),
                "cantidad": cantidad,
                "urgente": estado_actual == 0 and fecha_entrega_date <= hoy
            })

        if ordenes_a_actualizar:
            db.session.query(SolicitudProduccion).filter(
                SolicitudProduccion.detalleorden_id.in_(ordenes_a_actualizar)
            ).update(
                {SolicitudProduccion.estatus: 3},
                synchronize_session=False
            )
            db.session.commit()

        datos_ordenes.sort(key=lambda x: datetime.strptime(x['fecha'], '%d/%m/%Y %H:%M'))

        return render_template(
            "Orden/Ordenes.html",
            ordenes=datos_ordenes,
            active_page="ordenes"
        )

    except Exception as e:
        print(f"Error al obtener órdenes: {str(e)}")
        traceback.print_exc()
        return render_template(
            "Orden/Ordenes.html",
            ordenes=[],
            active_page="ordenes"
        )

#ruta que abre el detalle y receta dependiendo del id para saber las cantidades
@orden_bp.route("/detalles/<int:id_detalle>")
def detalles_receta(id_detalle):

    try:
        # detalle completo
        detalle_completo = obtener_detalle_orden(id_detalle)
        if not detalle_completo:
            print("No se encontro el detalle")
            flash("No se encontró el detalle de orden", "error")
            return redirect(url_for('orden.ordenes'))

        detalle, galleta, receta, orden, tipo_galleta = detalle_completo
        presentacion = tipo_galleta.nombre.lower()
        
        # Procesar ingredientes
        ingredientes = procesar_ingredientes(
            receta,
            receta.cantidad_galletas,
            detalle.cantidad,
            presentacion
        )
        
        # Preparar datos para vista
        datos_vista = {
            'receta': receta,
            'galleta': galleta,
            'cantidad': detalle.cantidad,
            'ingredientes': ingredientes,
            'orden': orden,
            'cantidad_base': receta.cantidad_galletas if receta.cantidad_galletas else 100,
            'active_page': "ordenes",
            'tipo_presentacion': presentacion,
            'total_galletas': ingredientes[0]['total_galletas'] if ingredientes else detalle.cantidad
        }

        if ingredientes:
            print(f"Total galletas calculado: {ingredientes[0].get('total_galletas', 'N/A')}")
            print(f"Insumo ejemplo: {ingredientes[0].get('insumo', 'N/A')} -> {ingredientes[0].get('cantidad_necesaria', 'N/A')}")

        return render_template("Orden/Orden_receta.html", **datos_vista)

    except Exception as e:

        print(f"Traceback: {traceback.format_exc()}")
        flash("Error al cargar los detalles", "error")
        return redirect(url_for('orden.ordenes'))

#ruta para abrir merma de insumos y carga todos los insumos y poner los lotes
@orden_bp.route("/merma_orden", methods=["GET", "POST"])
def merma_orden():
    form = MermaForm(request.form if request.method == "POST" else None)
    
    # Cargar insumos disponibles
    insumos = db.session.query(Insumos).filter(Insumos.total > 0).all()
    form.id_insumo.choices = [(i.id_insumo, f"{i.nombreInsumo} - {i.marca}") for i in insumos]
    
    try:
        if request.method == "POST":
            # Manejar lotes
            if 'cargar_lotes' in request.form:
                insumo_id = request.form.get('id_insumo')
                if insumo_id and insumo_id.isdigit():
                    lotes = db.session.query(LoteInsumo).filter(
                        LoteInsumo.id_insumo == int(insumo_id),
                        LoteInsumo.cantidad > 0
                    ).all()
                    form.id_lote.choices = [(l.idLote, f"Lote #{l.idLote} (Cad: {l.fechaCaducidad})") for l in lotes]
                    form.id_lote.render_kw = {}  # Habilitar select
                else:
                    form.id_lote.choices = []
                    form.id_lote.render_kw = {"disabled": True}
                
                # Mantener valores
                form.tipo.data = request.form.get('tipo')
                form.cantidad.data = request.form.get('cantidad')
                form.descripcion.data = request.form.get('descripcion')
                
                return render_template("Orden/Orden_merma.html", form=form)
            
            # Convertir Decimal
            try:
                cantidad_decimal = Decimal(str(form.cantidad.data))
            except:
                flash("Cantidad no válida", "error")
                return redirect(url_for("orden.merma_orden"))
            
            # opciones de lote antes de validar
            if form.id_insumo.data:
                lotes = db.session.query(LoteInsumo).filter(
                    LoteInsumo.id_insumo == form.id_insumo.data,
                    LoteInsumo.cantidad > 0
                ).all()
                form.id_lote.choices = [(l.idLote, f"Lote #{l.idLote} (Cad: {l.fechaCaducidad})") for l in lotes]
                form.id_lote.render_kw = {}
            
            if form.validate():
                lote = db.session.query(LoteInsumo).get(form.id_lote.data)
                if not lote:
                    flash("El lote seleccionado ya no está disponible", "error")
                    return redirect(url_for("orden.merma_orden"))
                
                # Convertir a Decimal
                lote_cantidad = Decimal(str(lote.cantidad))
                if lote_cantidad < cantidad_decimal:
                    flash("No hay suficiente stock en el lote seleccionado", "error")
                    return redirect(url_for("orden.merma_orden"))
                
                # Registrar merma
                merma = MermasInsumos(
                    lote_id=form.id_lote.data,
                    cantidad=float(cantidad_decimal),
                    tipo_merma=form.tipo.data,
                    descripcion=form.descripcion.data,
                    fecha=datetime.now().date()
                )
                
                # Actualizar stock
                lote.cantidad = float(lote_cantidad - cantidad_decimal)
                insumo = db.session.query(Insumos).get(form.id_insumo.data)
                insumo_total = Decimal(str(insumo.total))
                insumo.total = float(insumo_total - cantidad_decimal)
                
                db.session.add(merma)
                db.session.commit()
                
                flash("Merma registrada exitosamente", "success")
                return redirect(url_for("orden.merma_orden"))
            
            else:
                flash("Corrige los errores en el formulario", "error")
                print("Errores de validación:", form.errors)
    
    except Exception as e:
        db.session.rollback()
        flash(f"Error al procesar la merma: {str(e)}", "error")
        traceback.print_exc()
    
    return render_template("Orden/Orden_merma.html", active_page="ordenes", form=form)

#ruta para registrar la merma 
@orden_bp.route("/registrar_merma", methods=["GET", "POST"])
def registrar_merma():
    form = MermaForm(request.form)
    
    try:
        # Obtener insumos
        insumos = db.session.query(Insumos).filter(Insumos.total > 0).all()
        form.id_insumo.choices = [(i.id_insumo, f"{i.nombreInsumo} - {i.marca}") for i in insumos]
        
        if request.method == "POST":
            
            # hay lotes?
            is_cargar_lotes = 'cargar_lotes' in request.form and request.form['cargar_lotes'] == '1'
            
            # lotes SIEMPRE si hay insumo
            insumo_id = request.form.get('id_insumo')
            if insumo_id and insumo_id.isdigit():
                lotes = db.session.query(LoteInsumo).filter(
                    LoteInsumo.id_insumo == int(insumo_id),
                    LoteInsumo.cantidad > 0
                ).all()
                form.id_lote.choices = [(l.idLote, f"Lote #{l.idLote} (Cad: {l.fechaCaducidad})") for l in lotes]
            
            if is_cargar_lotes:
                form.tipo.data = request.form.get('tipo')
                form.cantidad.data = request.form.get('cantidad')
                form.descripcion.data = request.form.get('descripcion')
                return render_template("Orden/Orden_merma.html", form=form)
            
            # PROCESAR GUARDADO
            if form.validate():
                lote = db.session.query(LoteInsumo).get(form.id_lote.data)
                insumo = db.session.query(Insumos).get(form.id_insumo.data)
                
                cantidad = float(form.cantidad.data)
                if lote.cantidad < cantidad:
                    error_msg = f"Stock insuficiente. Disponible: {lote.cantidad}, Requerido: {cantidad}"
                    print(f"ERROR: {error_msg}")
                    flash(error_msg, "error")
                else:
                    merma = MermasInsumos(
                        lote_id=form.id_lote.data,
                        cantidad=cantidad,
                        tipo_merma=form.tipo.data,
                        descripcion=form.descripcion.data,
                        fecha=datetime.now().date()
                    )
                    
                    lote.cantidad -= cantidad
                    insumo.total -= cantidad
                    
                    db.session.add(merma)
                    db.session.commit()

                    flash("Merma registrada exitosamente", "success")
                    return redirect(url_for("orden.registrar_merma"))
            else:
                print("\nERRORES DE VALIDACIÓN:", form.errors)
                flash("Corrige los errores en el formulario", "error")
    
    except Exception as e:
        db.session.rollback()
        print(f"\nERROR: {str(e)}")
        traceback.print_exc()
        flash(f"Error al procesar: {str(e)}", "error")
    
    return render_template("Orden/Orden_merma.html", active_page="ordenes", form=form)

#ruta para cambiar el estatus y registrar en solicitud de produccion insertando los datos
@orden_bp.route("/completar/<int:id_detalle>", methods=['POST'])
def completar_orden(id_detalle):
    try:

        # Obtener el detalle de la orden con la presentacion
        detalle_completo = obtener_detalle_orden(id_detalle)
        if not detalle_completo:
            flash("Orden no encontrada", "error")
            return redirect(url_for('orden.ordenes'))

        detalle, galleta, receta, orden, tipo_galleta = detalle_completo
        presentacion = tipo_galleta.nombre.lower() if tipo_galleta else None
        
        # Procesar ingredientes coN LA PRESENTACION
        try:
            ingredientes = procesar_ingredientes(
                receta,
                receta.cantidad_galletas,
                detalle.cantidad,
                presentacion
            )
            
            for i in ingredientes:
                print(f"- {i.get('insumo')}: {i['cantidad_necesaria']} {i.get('unidad_original', 'unidades')}")
                print(f"  (Calculado para {i.get('total_galletas')} galletas)")
        except Exception as e:
            print(f"\nERROR procesando ingredientes: {str(e)}")
            flash("Error al calcular los ingredientes necesarios", "error")
            return redirect(url_for('orden.detalles_receta', id_detalle=id_detalle))

        try:
            # Descontar lotes
            for ingrediente in ingredientes:
                nombre_insumo = ingrediente.get('insumo')
                cantidad_necesaria = Decimal(str(ingrediente.get('cantidad_necesaria', 0)))
                unidad = ingrediente.get('unidad_original', 'unidades')
                
                if not nombre_insumo or cantidad_necesaria <= 0:
                    print(f"¡Datos incompletos para {nombre_insumo}! Saltando...")
                    continue

                print(f"\nProcesando: {nombre_insumo} - Necesarios: {cantidad_necesaria} {unidad}")

                insumo_db = Insumos.query.filter_by(nombreInsumo=nombre_insumo).first()
                if not insumo_db:
                    raise Exception(f"Insumo {nombre_insumo} no registrado")

                print(f"ID de insumo encontrado: {insumo_db.id_insumo}")

                # Buscar lotes disponibles
                lotes = db.session.query(LoteInsumo).filter(
                    LoteInsumo.id_insumo == insumo_db.id_insumo,
                    LoteInsumo.cantidad > 0
                ).order_by(LoteInsumo.fechaCaducidad.asc()).all()

                cantidad_restante = cantidad_necesaria
                print(f"Cantidad a descontar: {float(cantidad_restante)} {unidad}")
                print(f"Lotes disponibles: {len(lotes)}")

                for lote in lotes:
                    if cantidad_restante <= 0:
                        break

                    cantidad_disponible = Decimal(str(lote.cantidad))
                    cantidad_a_descontar = min(cantidad_restante, cantidad_disponible)
                    
                    # Actualizar lote
                    lote.cantidad = cantidad_disponible - cantidad_a_descontar
                    cantidad_restante -= cantidad_a_descontar
                    db.session.add(lote)
                    
                    print(f"  Descontado: {float(cantidad_a_descontar)} {unidad} del lote {lote.idLote}")

                # Actualizar insumos
                insumo_db.total = Decimal(str(insumo_db.total)) - (cantidad_necesaria - cantidad_restante)
                db.session.add(insumo_db)
                print(f"Total actualizado de {nombre_insumo}: {float(insumo_db.total)} {unidad}")

                if cantidad_restante > 0:
                    raise Exception(f"Stock insuficiente para {nombre_insumo} (faltan {float(cantidad_restante)} {unidad})")

            # Buscar o crear solicitud
            solicitud = SolicitudProduccion.query.filter_by(detalleorden_id=id_detalle).first()
            fecha_caducidad = datetime.now() + timedelta(days=8)

            if not solicitud:
                solicitud = SolicitudProduccion(
                    detalleorden_id=id_detalle,
                    estatus=1,
                    fechaCaducidad=fecha_caducidad.date()
                )
                db.session.add(solicitud)
                print("Nueva solicitud creada")
            else:
                solicitud.estatus = 1
                solicitud.fechaCaducidad = fecha_caducidad.date()
                print("Solicitud actualizada")

            db.session.commit()
            flash("Producción completada correctamente", "success")
            print("\n¡Producción completada con éxito!")

        except Exception as e:
            db.session.rollback()
            print(f"\n¡ERROR EN TRANSACCIÓN!: {str(e)}")
            traceback.print_exc()
            flash(f"Error al completar la producción: {str(e)}", "error")
            return redirect(url_for('orden.detalles_receta', id_detalle=id_detalle))

    except Exception as e:
        print(f"\n¡ERROR GENERAL!: {str(e)}")
        traceback.print_exc()
        flash("Error inesperado al procesar la solicitud", "error")
    
    return redirect(url_for('orden.ordenes'))
