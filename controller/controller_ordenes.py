
import ast
import math
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
from flask_login import login_required, current_user
from extensions import role_required
from datetime import datetime, timedelta
from sqlalchemy import desc, func, text
from extensions import db
from forms.ordenMermaGalleta_form import MermaGalletaform
from model.insumo import Insumos
from model.lote_insumo import LoteInsumo
from model.lote_galleta import LoteGalletas
from model.merma_galleta import MermaGalleta
from model.merma_insumo import MermasInsumos
from model.receta import Receta
from model.tipo_galleta import TipoGalleta
from model.galleta import Galleta
from model.detalle_venta_orden import DetalleVentaOrden
from model.orden import Orden
from model.solicitud_produccion import SolicitudProduccion
from forms.ordenMerma_form import MermaForm 
from decimal import Decimal

# Crear el Blueprint para orden
orden_bp = Blueprint("orden", __name__, url_prefix="/orden")

def estado_a_texto(estado):
    return {0: "INACTIVO", 1: "TERMINADO", 2: "ENTREGADO", 3: "LOTE"}.get(
        estado, "DESCONOCIDO"
    )


@login_required
@role_required("ADMS", "PROD") 
def obtener_detalle_orden(id_detalle):
    """Obtiene el detalle completo de la orden"""
    return (
        db.session.query(
            DetalleVentaOrden,
            Galleta,
            Receta,
            Orden,
            TipoGalleta,  # Añadimos TipoGalleta a la consulta
        )
        .join(Galleta, DetalleVentaOrden.galletas_id == Galleta.id_galleta)
        .join(Receta, Galleta.receta_id == Receta.idReceta)
        .join(Orden, DetalleVentaOrden.orden_id == Orden.id_orden)
        .join(
            TipoGalleta,
            Galleta.tipo_galleta_id
            == TipoGalleta.id_tipo_galleta,  # Unimos con TipoGalleta
        )
        .filter(DetalleVentaOrden.id_detalleVentaOrden == id_detalle)
        .first()
    )


@login_required
@role_required("ADMS", "PROD") 
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

@login_required
@role_required("ADMS", "PROD") 
def procesar_ingredientes(
    receta, cantidad_galletas, cantidad_pedido, presentacion=None, lotes_necesarios=1
):
    """Procesa ingredientes multiplicando por los lotes necesarios"""
    print(f"\n=== PROCESAR INGREDIENTES ===")
    print(f"Presentación recibida: {presentacion}")
    print(f"Cantidad pedido: {cantidad_pedido}")
    print(f"Lotes necesarios: {lotes_necesarios}")

    ingredientes = []
    try:
        if not receta.ingredientes:
            return ingredientes

        # Convertir lotes_necesarios a Decimal para operaciones consistentes
        lotes_necesarios = Decimal(str(lotes_necesarios))

        ingredientes_raw = parsear_ingredientes(receta.ingredientes)
        for ingrediente in ingredientes_raw:
            try:
                # Convertir la cantidad original a Decimal
                cantidad_original = Decimal(str(ingrediente["cantidad"]))
                cantidad_total = cantidad_original * lotes_necesarios

                ingrediente.update(
                    {
                        "cantidad_necesaria": float(
                            cantidad_total
                        ),  # Convertir a float para compatibilidad
                        "unidad_original": ingrediente.get("unidad", "unidades"),
                        "presentacion": presentacion,
                        "cantidad_cajas": (
                            cantidad_pedido
                            if presentacion in ["caja de kilo", "caja de 700 gramos"]
                            else None
                        ),
                        "total_galletas": (
                            cantidad_galletas if cantidad_galletas else 100
                        ),
                    }
                )

                print(
                    f"  - {ingrediente['insumo']}: {float(cantidad_original)} x {float(lotes_necesarios)} = {float(cantidad_total)} {ingrediente['unidad_original']}"
                )

            except (ValueError, KeyError) as e:
                print(f"¡Error procesando {ingrediente.get('insumo')}! {str(e)}")
                ingrediente["cantidad_necesaria"] = "N/A"

            ingredientes.append(ingrediente)

    except Exception as e:
        print(f"¡ERROR en procesar_ingredientes! {str(e)}")
        raise

    print("=== FIN DE PROCESAR INGREDIENTES ===\n")
    return ingredientes

@login_required
@role_required("ADMS", "PROD") 
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
            print(
                f"La orden {id_orden} ha pasado su fecha de entrega ({fecha_entrega})"
            )

            # Actualizar todas las solicitudes relacionadas con esta orden
            solicitudes = (
                db.session.query(SolicitudProduccion)
                .join(
                    DetalleVentaOrden,
                    SolicitudProduccion.detalleorden_id
                    == DetalleVentaOrden.id_detalleVentaOrden,
                )
                .filter(
                    DetalleVentaOrden.orden_id == id_orden,
                    SolicitudProduccion.estatus.in_(
                        [0, 1]
                    ),  # Solo INACTIVO o TERMINADO
                )
                .all()
            )

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
                    detalle_orden.cantidad, presentacion
                )

                # Insertar en lote_galletas
                insertar_lote_galleta(
                    galleta.id_galleta, cantidad_total, solicitud.fechaCaducidad
                )

            db.session.commit()
            return True

        return False

    except Exception as e:
        print(f"Error al verificar estatus de orden {id_orden}: {str(e)}")
        traceback.print_exc()
        db.session.rollback()
        return False

@login_required
@role_required("ADMS", "PROD") 
def calcular_cantidad_total_galletas(cantidad_pedido, presentacion):
    """Calcula la cantidad total de galletas según la presentación"""
    if presentacion.lower() == "caja de kilo":
        return int(cantidad_pedido * 27)  # 27 galletas por caja
    elif presentacion.lower() == "caja de 700":
        return int(cantidad_pedido * 19)  # 19 galletas por caja
    else:
        return int(cantidad_pedido)  # Unidades individuales

@login_required
@role_required("ADMS", "PROD")
def insertar_lote_galleta(galleta_id, cantidad, fecha_caducidad):
    """Inserta un nuevo registro en la tabla lotesGalletas"""
    try:
        # Calcular fecha de produccion
        fecha_produccion = fecha_caducidad - timedelta(days=7)

        # costo de produccion
        costo_total = cantidad * Decimal("4.5")

        # Crear el nuevo lote
        nuevo_lote = LoteGalletas(
            galleta_id=galleta_id,
            cantidad=cantidad,
            costo=costo_total,
            existencia=cantidad,
            fechaProduccion=fecha_produccion,
            fechaCaducidad=fecha_caducidad,
        )

        db.session.add(nuevo_lote)
        db.session.commit()
        print(
            f"Nuevo lote creado: {nuevo_lote.id_lote} con costo de {costo_total} por {cantidad} galletas"
        )
        return True
    except Exception as e:
        print(f"Error al insertar lote de galletas: {str(e)}")
        db.session.rollback()
        return False

@login_required
@role_required("ADMS", "PROD")
def calcular_produccion_necesaria(
    cantidad_pedido, tipo_presentacion, inventario, cantidad_por_lote
):
    """Calcula la producción necesaria usando solo la presentación solicitada"""
    # Convertir todo a galletas individuales según la presentación
    tipo_presentacion = tipo_presentacion.lower()
    
    if tipo_presentacion == "caja de kilo":
        galletas_por_presentacion = 27
        presentacion_disponible = inventario.get("cajas_kilo", 0) * galletas_por_presentacion
    elif tipo_presentacion == "caja de 700 gramos":
        galletas_por_presentacion = 19
        presentacion_disponible = inventario.get("cajas_700", 0) * galletas_por_presentacion
    else:  # Unidades
        galletas_por_presentacion = 1
        presentacion_disponible = inventario.get("unidades", 0)

    galletas_solicitadas = cantidad_pedido * galletas_por_presentacion
    galletas_cubiertas = min(presentacion_disponible, galletas_solicitadas)
    
    # Calcular presentaciones usadas
    if galletas_por_presentacion > 1:  # Para cajas
        presentaciones_usadas = galletas_cubiertas // galletas_por_presentacion
    else:  # Para unidades
        presentaciones_usadas = galletas_cubiertas

    # Calcular el faltante
    faltante = max(0, galletas_solicitadas - galletas_cubiertas)

    # Calcular lotes necesarios
    lotes_necesarios = math.ceil(faltante / cantidad_por_lote) if faltante > 0 else 0

    return {
        "presentaciones_usadas": presentaciones_usadas,
        "unidades_usadas": presentaciones_usadas if galletas_por_presentacion == 1 else 0,
        "cajas_usadas": presentaciones_usadas if galletas_por_presentacion > 1 else 0,
        "lotes_necesarios": lotes_necesarios,
        "faltante": faltante,
        "galletas_solicitadas": galletas_solicitadas,
        "galletas_cubiertas": galletas_cubiertas,
        "presentacion_solicitada": tipo_presentacion,
        "galletas_por_presentacion": galletas_por_presentacion,
    }


@login_required
@role_required("ADMS", "PROD")
def obtener_inventario_tabla(nombre_galleta):
    """Obtiene el inventario en formato de tabla para una galleta específica"""
    query = text(
        """
        SELECT 
            tg.nombre AS tipo_galleta,
            g.galleta AS nombre_galleta,
            SUM(lg.existencia) AS total_existencia
        FROM tipo_galleta tg
        JOIN galletas g ON tg.id_tipo_galleta = g.tipo_galleta_id
        JOIN lotesGalletas lg ON g.id_galleta = lg.galleta_id
        WHERE 
            lg.fechaCaducidad >= CURRENT_DATE
            AND g.galleta = :nombre_galleta
        GROUP BY tg.nombre, g.galleta
        ORDER BY tg.nombre;
    """
    )

    inventario = db.session.execute(
        query, {"nombre_galleta": nombre_galleta}
    ).fetchall()

    return inventario

@login_required
@role_required("ADMS", "PROD")
def procesar_ingredientes_sin_modificacion(receta):
    """Procesa ingredientes mostrando exactamente las cantidades de la receta"""
    ingredientes = []
    try:
        if not receta.ingredientes:
            return ingredientes

        ingredientes_raw = parsear_ingredientes(receta.ingredientes)
        for ingrediente in ingredientes_raw:
            try:
                # Mantener todos los datos originales sin cambios
                ingrediente.update(
                    {
                        "cantidad_necesaria": float(ingrediente["cantidad"]),
                        "total_galletas": (
                            receta.cantidad_galletas
                            if receta.cantidad_galletas
                            else 100
                        ),
                        "presentacion": None,
                        "cantidad_cajas": None,
                    }
                )
            except (ValueError, KeyError) as e:
                print(f"Error procesando ingrediente: {str(e)}")
                ingrediente["cantidad_necesaria"] = "N/A"

            ingredientes.append(ingrediente)

    except Exception as e:
        print(f"Error en procesar_ingredientes_sin_modificacion: {str(e)}")
        raise

    return ingredientes

@login_required
@role_required("ADMS", "PROD")
def calcular_inventario_galletas(galleta_id):
    """Calcula el inventario de galletas sumando todos los lotes válidos"""
    inventario = {"unidades": 0, "cajas_kilo": 0, "cajas_700": 0, "total_unidades": 0}

    # Sumar existencias de todos los lotes no vencidos
    lotes = LoteGalletas.query.filter(
        LoteGalletas.galleta_id == galleta_id,
        LoteGalletas.existencia > 0,
        LoteGalletas.fechaCaducidad >= datetime.now().date(),
    ).all()

    for lote in lotes:
        if lote.cantidad == 27:  # Caja de 1kg
            inventario["cajas_kilo"] += lote.existencia
        elif lote.cantidad == 19:  # Caja de 700g
            inventario["cajas_700"] += lote.existencia
        else:  # Unidades sueltas
            inventario["unidades"] += lote.existencia

        inventario["total_unidades"] += lote.existencia

    return inventario

@login_required
@role_required("ADMS", "PROD")
def obtener_id_galleta_por_orden(id_detalle):
    """Obtiene el id_galleta a partir del id_detalle usando tu estructura SQL"""
    resultado = db.session.execute(
        text(
            """
        SELECT g.id_galleta
        FROM detalleVentaOrden dvo
        JOIN galletas g ON dvo.galletas_id = g.id_galleta
        WHERE dvo.id_detalleVentaOrden = :id_detalle
        """
        ),
        {"id_detalle": id_detalle},
    ).fetchone()

    return resultado[0] if resultado else None







#ruta principal donde muestra los pedidos y llama las funciones anteirores para las fechas y los estatus y agregar a lotes
@orden_bp.route("/")
@login_required
@role_required("ADMS", "PROD") 
def ordenes():
    try:
        # fecha actual
        hoy = datetime.now().date()

        resultados = (
            db.session.query(
                DetalleVentaOrden.id_detalleVentaOrden.label("id_detalle"),
                Galleta.galleta,
                Orden.fechaEntrega,
                SolicitudProduccion.estatus,
                DetalleVentaOrden.cantidad,
                Orden.id_orden,
            )
            .join(Galleta, DetalleVentaOrden.galletas_id == Galleta.id_galleta)
            .join(Orden, DetalleVentaOrden.orden_id == Orden.id_orden)
            .outerjoin(
                SolicitudProduccion,
                DetalleVentaOrden.id_detalleVentaOrden
                == SolicitudProduccion.detalleorden_id,
            )
            .filter(
                (SolicitudProduccion.estatus.in_([0, 1]))
                | (SolicitudProduccion.estatus == None)
            )
            .order_by(Orden.fechaEntrega.asc())
            .all()
        )

        # Verificamos ordenes vencidas
        ordenes_procesadas = set()

        for _, _, _, _, _, id_orden in resultados:
            if id_orden not in ordenes_procesadas:
                verificar_actualizar_estatus_orden(id_orden)
                ordenes_procesadas.add(id_orden)

        ordenes_a_actualizar = []
        datos_ordenes = []

        for (
            id_detalle,
            nombre_galleta,
            fecha_entrega,
            estatus,
            cantidad,
            _,
        ) in resultados:
            estado_actual = estatus if estatus is not None else 0
            fecha_entrega_date = fecha_entrega.date()

            if estado_actual == 1 and fecha_entrega_date < hoy:
                ordenes_a_actualizar.append(id_detalle)

            datos_ordenes.append(
                {
                    "id_detalle": id_detalle,
                    "galleta": nombre_galleta,
                    "fecha": fecha_entrega.strftime("%d/%m/%Y %H:%M"),
                    "estado": estado_a_texto(estado_actual),
                    "cantidad": cantidad,
                    "urgente": estado_actual == 0 and fecha_entrega_date <= hoy,
                }
            )

        if ordenes_a_actualizar:
            db.session.query(SolicitudProduccion).filter(
                SolicitudProduccion.detalleorden_id.in_(ordenes_a_actualizar)
            ).update({SolicitudProduccion.estatus: 3}, synchronize_session=False)
            db.session.commit()

        datos_ordenes.sort(
            key=lambda x: datetime.strptime(x["fecha"], "%d/%m/%Y %H:%M")
        )

        return render_template(
            "Orden/Ordenes.html",
            ordenes=datos_ordenes,
            obtener_id_galleta_por_orden=obtener_id_galleta_por_orden,
            active_page="ordenes",
        )

    except Exception as e:
        print(f"Error al obtener órdenes: {str(e)}")
        traceback.print_exc()
        return render_template("Orden/Ordenes.html", ordenes=[], active_page="ordenes")


#ruta que abre el detalle y receta dependiendo del id para saber las cantidades
@orden_bp.route("/detalles/<int:id_detalle>")
@login_required
@role_required("ADMS", "PROD") 
def detalles_receta(id_detalle):
    try:
        # Obtener datos básicos de la orden
        detalle, galleta, receta, orden, tipo_galleta = obtener_detalle_orden(
            id_detalle
        )
        presentacion = tipo_galleta.nombre if tipo_galleta else "Unidad"

        # Obtener inventario en formato de tabla
        inventario_tabla = obtener_inventario_tabla(galleta.galleta)

        # Convertir a formato de diccionario para compatibilidad
        inventario = {
            "unidades": 0,
            "cajas_kilo": 0,
            "cajas_700": 0,
            "total_unidades": 0,
        }

        # Procesar resultados del inventario
        for item in inventario_tabla:
            tipo = item.tipo_galleta.lower()
            if "unidad" in tipo:
                inventario["unidades"] = item.total_existencia
                inventario["total_unidades"] += item.total_existencia
            elif "kilo" in tipo:
                inventario["cajas_kilo"] = item.total_existencia
                inventario["total_unidades"] += item.total_existencia * 27
            elif "700" in tipo:
                inventario["cajas_700"] = item.total_existencia
                inventario["total_unidades"] += item.total_existencia * 19

        # Obtener cantidad por lote de la receta (valor por defecto 100 si no está definido)
        cantidad_por_lote = (
            receta.cantidad_galletas if receta.cantidad_galletas else 100
        )

        # Calcular producción necesaria
        produccion = calcular_produccion_necesaria(
            detalle.cantidad, presentacion, inventario, cantidad_por_lote
        )

        # Procesar ingredientes SIN modificar cantidades
        ingredientes = procesar_ingredientes_sin_modificacion(receta)

        # Calcular total de galletas para mostrar
        if presentacion.lower() == "caja de kilo":
            total_galletas = detalle.cantidad * 27
        elif presentacion.lower() == "caja de 700 gramos":
            total_galletas = detalle.cantidad * 19
        else:
            total_galletas = detalle.cantidad

        return render_template(
            "Orden/Orden_receta.html",
            receta=receta,
            cantidad=detalle.cantidad,
            ingredientes=ingredientes,
            tipo_presentacion=presentacion,
            produccion=produccion,
            inventario=inventario,
            inventario_tabla=inventario_tabla,
            total_galletas=total_galletas,
            cantidad_por_lote=cantidad_por_lote,
            active_page="ordenes",
        )

    except Exception as e:
        flash(f"Error al cargar los detalles: {str(e)}", "error")
        return redirect(url_for("orden.ordenes"))


#ruta para abrir merma de insumos y carga todos los insumos y poner los lotes
@orden_bp.route("/merma_orden", methods=["GET", "POST"])
@login_required
@role_required("ADMS", "PROD") 
def merma_orden():
    form = MermaForm(request.form if request.method == "POST" else None)

    # Cargar insumos disponibles
    insumos = db.session.query(Insumos).filter(Insumos.total > 0).all()
    form.id_insumo.choices = [
        (i.id_insumo, f"{i.nombreInsumo} - {i.marca}") for i in insumos
    ]

    try:
        if request.method == "POST":
            # Manejar lotes
            if "cargar_lotes" in request.form:
                insumo_id = request.form.get("id_insumo")
                if insumo_id and insumo_id.isdigit():
                    lotes = (
                        db.session.query(LoteInsumo)
                        .filter(
                            LoteInsumo.id_insumo == int(insumo_id),
                            LoteInsumo.cantidad > 0,
                        )
                        .all()
                    )
                    form.id_lote.choices = [
                        (l.idLote, f"Lote #{l.idLote} (Cad: {l.fechaCaducidad})")
                        for l in lotes
                    ]
                    form.id_lote.render_kw = {}  # Habilitar select
                else:
                    form.id_lote.choices = []
                    form.id_lote.render_kw = {"disabled": True}

                # Mantener valores
                form.tipo.data = request.form.get("tipo")
                form.cantidad.data = request.form.get("cantidad")
                form.descripcion.data = request.form.get("descripcion")

                return render_template("Orden/Orden_merma.html", form=form)

            # Convertir Decimal
            try:
                cantidad_decimal = Decimal(str(form.cantidad.data))
            except:
                flash("Cantidad no válida", "error")
                return redirect(url_for("orden.merma_orden"))

            # opciones de lote antes de validar
            if form.id_insumo.data:
                lotes = (
                    db.session.query(LoteInsumo)
                    .filter(
                        LoteInsumo.id_insumo == form.id_insumo.data,
                        LoteInsumo.cantidad > 0,
                    )
                    .all()
                )
                form.id_lote.choices = [
                    (l.idLote, f"Lote #{l.idLote} (Cad: {l.fechaCaducidad})")
                    for l in lotes
                ]
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
                    fecha=datetime.now().date(),
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
@login_required
@role_required("ADMS", "PROD") 
def registrar_merma():
    form = MermaForm(request.form)

    try:
        # Obtener insumos
        insumos = db.session.query(Insumos).filter(Insumos.total > 0).all()
        form.id_insumo.choices = [
            (i.id_insumo, f"{i.nombreInsumo} - {i.marca}") for i in insumos
        ]

        if request.method == "POST":

            # hay lotes?
            is_cargar_lotes = (
                "cargar_lotes" in request.form and request.form["cargar_lotes"] == "1"
            )

            # lotes SIEMPRE si hay insumo
            insumo_id = request.form.get("id_insumo")
            if insumo_id and insumo_id.isdigit():
                lotes = (
                    db.session.query(LoteInsumo)
                    .filter(
                        LoteInsumo.id_insumo == int(insumo_id), LoteInsumo.cantidad > 0
                    )
                    .all()
                )
                form.id_lote.choices = [
                    (l.idLote, f"Lote #{l.idLote} (Cad: {l.fechaCaducidad})")
                    for l in lotes
                ]

            if is_cargar_lotes:
                form.tipo.data = request.form.get("tipo")
                form.cantidad.data = request.form.get("cantidad")
                form.descripcion.data = request.form.get("descripcion")
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
                        fecha=datetime.now().date(),
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
@login_required
@role_required("ADMS", "PROD") 
def completar_orden(id_detalle):
    try:
        # Obtener el detalle completo de la orden
        detalle_completo = obtener_detalle_orden(id_detalle)
        if not detalle_completo:
            flash("Orden no encontrada", "error")
            return redirect(url_for("orden.ordenes"))

        detalle, galleta, receta, orden, tipo_galleta = detalle_completo
        presentacion = tipo_galleta.nombre.lower() if tipo_galleta else "unidad"

        # Obtener la cantidad_galletas de la receta asociada
        cantidad_galletas_por_lote = (
            receta.cantidad_galletas if receta else 100
        )  # Valor por defecto de 100 si no se encuentra receta

        # Verificar si ya fue producida
        solicitud_existente = SolicitudProduccion.query.filter(
            SolicitudProduccion.detalleorden_id == id_detalle,
            SolicitudProduccion.estatus >= 1,
        ).first()

        if solicitud_existente:
            flash("Esta orden ya fue producida anteriormente", "error")
            return redirect(url_for("orden.detalles_receta", id_detalle=id_detalle))

        # Calcular la cantidad de productos solicitados
        galletas_solicitadas = detalle.cantidad

        # Obtener inventario actual
        inventario = calcular_inventario_galletas(galleta.id_galleta)

        # Verificar si hay suficiente inventario
        if inventario["total_unidades"] >= galletas_solicitadas:
            # Si hay suficiente inventario, registrar como producción completada
            try:
                # Registrar la solicitud de producción como completada
                solicitud = SolicitudProduccion(
                    detalleorden_id=id_detalle,
                    estatus=1,  # Terminada
                    fechaCaducidad=datetime.now().date() + timedelta(days=7),
                )
                db.session.add(solicitud)

                # Confirmar la transacción
                db.session.commit()

                flash(
                    "La orden se ha completado con el inventario existente y se ha registrado como producida.",
                    "success",
                )

            except Exception as e:
                db.session.rollback()
                flash(f"Error al registrar la producción: {str(e)}", "error")
                return redirect(url_for("orden.detalles_receta", id_detalle=id_detalle))

        else:
            # Si no hay suficiente inventario, proceder con la producción
            cantidad_faltante = galletas_solicitadas - inventario["total_unidades"]

            if presentacion == "caja de kilo":
                cajas_de_kilo_disponibles = inventario.get("cajas_kilo", 0)

                # Verificar si hay suficientes cajas de kilo
                if cajas_de_kilo_disponibles >= galletas_solicitadas:
                    cantidad_faltante = 0  # No faltan cajas de kilo
                else:
                    cantidad_faltante = galletas_solicitadas - cajas_de_kilo_disponibles

            elif presentacion == "caja de 700 gramos":
                cajas_de_700_disponibles = inventario.get("cajas_700", 0)

                # Verificar si hay suficientes cajas de 700 gramos
                if cajas_de_700_disponibles >= galletas_solicitadas:
                    cantidad_faltante = 0  # No faltan cajas de 700 gramos
                else:
                    cantidad_faltante = galletas_solicitadas - cajas_de_700_disponibles

            if cantidad_faltante == 0:
                # Si no falta nada, simplemente se confirma que ya hay suficientes cajas
                flash(f"Ya hay suficientes {presentacion} disponibles.", "success")
            else:
                # Si falta, producir la cantidad faltante
                try:
                    # **Nuevo ajuste para unidades: Respetar los lotes completos**
                    if presentacion == "unidad":
                        # Usar cantidad_galletas de la receta para definir el tamaño del lote
                        lote_size = cantidad_galletas_por_lote

                        # Calcular cuántos lotes completos se necesitan
                        lotes_necesarios = (
                            cantidad_faltante + lote_size - 1
                        ) // lote_size  # Redondear hacia arriba
                        cantidad_a_producir = lotes_necesarios * lote_size

                        lote_galletas = LoteGalletas(
                            galleta_id=galleta.id_galleta,
                            cantidad=cantidad_a_producir,
                            costo=cantidad_a_producir
                            * Decimal("1.0"),  # Ajusta el costo según corresponda
                            existencia=cantidad_a_producir,
                            fechaProduccion=datetime.now().date(),
                            fechaCaducidad=datetime.now().date() + timedelta(days=7),
                        )

                    elif presentacion == "caja de kilo":
                        cantidad_a_producir = cantidad_faltante  # No se multiplica la cantidad de galletas producidas

                        lote_galletas = LoteGalletas(
                            galleta_id=galleta.id_galleta,
                            cantidad=cantidad_a_producir,
                            costo=cantidad_a_producir
                            * Decimal("4.5"),  # Ajusta el costo según corresponda
                            existencia=cantidad_a_producir,
                            fechaProduccion=datetime.now().date(),
                            fechaCaducidad=datetime.now().date() + timedelta(days=7),
                        )

                    elif presentacion == "caja de 700 gramos":
                        cantidad_a_producir = cantidad_faltante  # No se multiplica la cantidad de galletas producidas

                        lote_galletas = LoteGalletas(
                            galleta_id=galleta.id_galleta,
                            cantidad=cantidad_a_producir,
                            costo=cantidad_a_producir
                            * Decimal("3.2"),  # Ajusta el costo según corresponda
                            existencia=cantidad_a_producir,
                            fechaProduccion=datetime.now().date(),
                            fechaCaducidad=datetime.now().date() + timedelta(days=7),
                        )

                    db.session.add(lote_galletas)

                    # Registrar la solicitud de producción
                    solicitud = SolicitudProduccion(
                        detalleorden_id=id_detalle,
                        estatus=1,  # Terminada
                        fechaCaducidad=datetime.now().date() + timedelta(days=7),
                    )
                    db.session.add(solicitud)

                    # **Corregir aquí**: Sumar la cantidad producida al inventario en la tabla Galleta
                    galleta.existencia += cantidad_a_producir  # Se usa cantidad_a_producir para las cajas

                    # Descontar los insumos necesarios de loteinsumo y de insumos
                    ingredientes = procesar_ingredientes(
                        receta, cantidad_galletas_por_lote, cantidad_a_producir
                    )

                    for ingrediente in ingredientes:
                        if ingrediente.get("insumo"):
                            # Descontar el ingrediente de loteinsumo
                            lote_insumo = (
                                LoteInsumo.query.join(Insumos)
                                .filter(Insumos.nombreInsumo == ingrediente["insumo"])
                                .first()
                            )

                            if lote_insumo:
                                lote_insumo.cantidad -= ingrediente["cantidad_necesaria"]

                            # Descontar el ingrediente de la tabla insumos
                            insumo = Insumos.query.filter(
                                Insumos.nombreInsumo == ingrediente["insumo"]
                            ).first()

                            if insumo:
                                if presentacion in ["caja de kilo", "caja de 700 gramos"]:
                                    ingrediente["cantidad_necesaria"] *= 2  # Multiplicar por 2 solo los insumos
                                insumo.total -= ingrediente["cantidad_necesaria"]

                    db.session.commit()

                    flash(
                        f"Se produjeron las galletas con exito y los insumos fueron descontados",
                        "success",
                    )

                except Exception as e:
                    db.session.rollback()
                    flash(f"Error al procesar la producción: {str(e)}", "error")
                    return redirect(
                        url_for("orden.detalles_receta", id_detalle=id_detalle)
                    )

        return redirect(url_for("orden.ordenes"))

    except Exception as e:
        # Manejo de error general
        flash(f"Error general: {str(e)}", "error")
        return redirect(url_for("orden.ordenes"))


@orden_bp.route("/merma_galleta/<int:galleta_id>", methods=["GET", "POST"])
@login_required
@role_required("ADMS", "PROD") 
def merma_galleta(galleta_id):
    form = MermaGalletaform(request.form if request.method == "POST" else None)

    try:
        galleta = Galleta.query.get_or_404(galleta_id)
        form.id_galleta.data = galleta_id

        # CORRECCIÓN: Cambiar filter_by con existencia__gt por filter con expresión estándar
        lote = (
            LoteGalletas.query.filter(
                LoteGalletas.galleta_id == galleta_id,
                LoteGalletas.existencia > 0,  # Forma correcta para SQLAlchemy
            )
            .order_by(desc(LoteGalletas.id_lote))
            .first()
        )

        if lote:
            form.id_lote.choices = [
                (
                    lote.id_lote,
                    f"Lote #{lote.id_lote} (Cad: {lote.fechaCaducidad.strftime('%d/%m/%Y')} - Exist: {lote.existencia})",
                )
            ]
            form.id_lote.data = lote.id_lote

        if request.method == "POST" and form.validate():
            cantidad = float(form.cantidad.data)

            if lote.existencia < cantidad:
                flash(
                    f"No hay suficiente stock. Existencia: {lote.existencia}", "error"
                )
                return redirect(url_for("orden.merma_galleta", galleta_id=galleta_id))

            merma = MermaGalleta(
                lote_id=lote.id_lote,
                cantidad=cantidad,
                tipo_merma=form.tipo_merma.data,
                descripcion=form.descripcion.data,
                fecha=datetime.now().date(),
            )

            lote.existencia -= cantidad
            galleta.existencia -= cantidad

            db.session.add(merma)
            db.session.commit()

            flash("Merma registrada correctamente", "success")
            return redirect(url_for("orden.ordenes"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar merma: {str(e)}", "error")
        traceback.print_exc()

    return render_template(
        "Orden/orden_merma_galleta.html",
        form=form,
        galleta=galleta,
        active_page="ordenes",
    )


@orden_bp.route("/get_lotes_galleta/<int:galleta_id>")
@login_required
@role_required("ADMS", "PROD") 
def get_lotes_galleta(galleta_id):
    try:
        lotes = LoteGalletas.query.filter(
            LoteGalletas.galleta_id == galleta_id,
            LoteGalletas.existencia > 0,
            LoteGalletas.fechaCaducidad >= datetime.now().date(),
        ).all()

        return jsonify(
            {
                "lotes": [
                    {
                        "id": l.id_lote,
                        "caducidad": l.fechaCaducidad.strftime("%Y-%m-%d"),
                        "existencia": l.existencia,
                    }
                    for l in lotes
                ]
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@orden_bp.route("/guardar_merma_galleta", methods=["POST"])
@login_required
@role_required("ADMS", "PROD") 
def guardar_merma_galleta():
    form = MermaGalletaform(request.form)

    # Habilitar temporalmente el campo id_lote para validación
    form.id_lote.render_kw = {}

    # Validación manual equivalente a validate_on_submit()
    if request.method == "POST" and form.validate():
        try:
            # Obtener datos del formulario
            lote_id = form.id_lote.data
            cantidad = float(form.cantidad.data)
            galleta_id = form.id_galleta.data

            # Obtener el lote y la galleta asociada
            lote = LoteGalletas.query.get_or_404(lote_id)
            galleta = Galleta.query.get_or_404(galleta_id)

            # Validar existencia suficiente
            if lote.existencia < cantidad:
                flash(
                    f"No hay suficiente stock. Existencia: {lote.existencia}", "error"
                )
                return redirect(url_for("orden.merma_galleta", galleta_id=galleta_id))

            # Registrar la merma
            nueva_merma = MermaGalleta(
                lote_id=lote_id,
                cantidad=cantidad,
                tipo_merma=form.tipo_merma.data,
                descripcion=form.descripcion.data,
                fecha=datetime.now().date(),
            )

            # Actualizar existencias
            lote.existencia -= cantidad
            galleta.existencia -= cantidad

            # Guardar cambios
            db.session.add(nueva_merma)
            db.session.commit()

            flash("Merma registrada correctamente", "success")
            return redirect(url_for("orden.ordenes"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar merma: {str(e)}", "error")
            print(f"Error: {str(e)}")
            traceback.print_exc()
            return redirect(url_for("orden.merma_galleta", galleta_id=galleta_id))

    # Si el formulario no es válido
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error en {getattr(form, field).label.text}: {error}", "error")
    return redirect(
        url_for("orden.merma_galleta", galleta_id=request.form.get("galleta_id"))
    )
