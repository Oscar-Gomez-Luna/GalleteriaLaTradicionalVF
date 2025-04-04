
from flask import (Blueprint,Flask,render_template,request,redirect,url_for,flash,session,)
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from extensions import role_required
from sqlalchemy import desc, func
from extensions import db
from model.insumo import Insumos
from model.proveedor import Proveedor
from model.compraRealizada import ComprasRealizadas
from model.detalleCompra import DetalleCompra
from model.lote_insumo import LoteInsumo
from model.merma_insumo import MermasInsumos
from forms.registrarInsumo_form import RegistrarInsumo
from forms.ordenCompra_form import OrdenCompraForm, DynamicFechaCaducidadForm
from forms.insumosMerma_form import InsumosMerma
from forms.comprarInsumos_form import ComprarInsumos


# Crear el Blueprint para insumos
insumo_bp = Blueprint("insumo", __name__, url_prefix="/insumos")

#Metodo para decscontar los lotes caducados
@login_required
@role_required("ADMS", "PROD")
def descontar_lotes_caducados():
    """Metodo para descontar lotes que han alcanzado su fecha de caducidad"""
    hoy = datetime.now().date()
    lotes_caducados = LoteInsumo.query.filter(
        LoteInsumo.fechaCaducidad == hoy,
        LoteInsumo.cantidad > 0  # Solo lotes que aun tienen cantidad
    ).all()

    for lote in lotes_caducados:
        try:
            
            insumo = lote.insumo
            insumo.total -= lote.cantidad
            
            # Poner la cantidad del lote a 0
            lote.cantidad = 0
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al descontar lote caducado: {e}")

#ruta principal que muestra la tabla, carga el modal de lo que se debe, los ordenes y lo del metodo de descontar, y las alertas
@insumo_bp.route("/", methods=["GET", "POST"])
@login_required
@role_required("ADMS", "PROD")
def insumos():
    # Primero verificamos para descontar los lotes caducados
    descontar_lotes_caducados()

    if request.method == "POST":
        filtro = request.form.get("filtro_insumo")
        if filtro:
            lista_insumos = Insumos.query.filter(
                Insumos.nombreInsumo.ilike(f"%{filtro}%")
            ).all()
        else:
            lista_insumos = Insumos.query.all()
    else:
        lista_insumos = Insumos.query.all()

    alertas = []

    # 1. Alertas insumos por terminarse
    for insumo in lista_insumos:
        unidad = insumo.unidad.lower()

        if any(u in unidad for u in ["gramo", "mililitro"]) and insumo.total < 10000:
            alertas.append(
                f"{insumo.nombreInsumo} está por terminarse (Quedan {insumo.total} {insumo.unidad})"
            )
        elif "unidad" in unidad and insumo.total < 100:
            alertas.append(
                f"{insumo.nombreInsumo} está por terminarse (Quedan {insumo.total} unidades)"
            )

    # 2. Alertas lotes caducar (7 días)
    fecha_limite_caducidad = datetime.now().date() + timedelta(days=7)
    lotes_por_caducar = (
        LoteInsumo.query.filter(
            LoteInsumo.fechaCaducidad <= fecha_limite_caducidad,
            LoteInsumo.fechaCaducidad >= datetime.now().date(),
            LoteInsumo.cantidad > 0
        )
        .join(Insumos)
        .all()
    )

    for lote in lotes_por_caducar:
        dias_restantes = (lote.fechaCaducidad - datetime.now().date()).days
        alertas.append(
            f"Lote de {lote.insumo.nombreInsumo} caduca en {dias_restantes} días ({lote.fechaCaducidad.strftime('%d/%m/%Y')})"
        )

    # 3. Alertas lotes caducados ya
    lotes_caducados_hoy = LoteInsumo.query.filter(
        LoteInsumo.fechaCaducidad == datetime.now().date(),
        LoteInsumo.cantidad == 0
    ).join(Insumos).all()

    for lote in lotes_caducados_hoy:
        alertas.append(
            f"Lote de {lote.insumo.nombreInsumo} caduco hoy y fue descontado del inventario"
        )

    # Datos para el resumen de pagos
    fecha_limite = datetime.now() - timedelta(days=7)

    compras_semana = (
        db.session.query(
            Proveedor.empresa.label("NombreEmpresa"),
            func.sum(ComprasRealizadas.precio).label("TotalVenta"),
        )
        .join(
            ComprasRealizadas, Proveedor.id_proveedor == ComprasRealizadas.id_proveedor
        )
        .filter(ComprasRealizadas.estatus == 1, ComprasRealizadas.fecha >= fecha_limite)
        .group_by(Proveedor.empresa)
        .order_by(func.sum(ComprasRealizadas.precio).desc())
        .all()
    )

    # Datos modal de ordenes
    ordenes_compra = (
        db.session.query(
            Proveedor.empresa.label("NombreEmpresa"),
            ComprasRealizadas.numeroOrden,
            ComprasRealizadas.precio.label("Total"),
            ComprasRealizadas.fecha,
        )
        .join(Proveedor, Proveedor.id_proveedor == ComprasRealizadas.id_proveedor)
        .filter(ComprasRealizadas.estatus == 0, ComprasRealizadas.fecha >= fecha_limite)
        .order_by(desc(ComprasRealizadas.fecha))
        .all()
    )

    return render_template(
        "Insumos/Insumos.html",
        insumos=lista_insumos,
        compras=compras_semana,
        ordenes_compra=ordenes_compra,
        alertas=alertas,
        active_page="insumos",
        usuario = current_user
    )

#ruta para registrar un nuevo insumo que trae el nombre del proveedor
@insumo_bp.route("/registrar", methods=["GET", "POST"])
@login_required
@role_required("ADMS", "PROD")
def registrar_insumo():
    create_form = RegistrarInsumo(request.form)

    try:
        # proveedores activos
        proveedor = Proveedor.query.filter_by(estatus=1).all()
        proveedor_options = [(p.id_proveedor, p.empresa) for p in proveedor]

        # Opciones para los select
        create_form.id_proveedor.choices = proveedor_options
        create_form.unidad.choices = [
            ("Gramos", "Gramos"),
            ("Mililitros", "Mililitros"),
            ("Unidad", "Unidad"),
        ]

        if request.method == "POST" and create_form.validate():
            nuevo_insumo = Insumos(
                nombreInsumo=create_form.nombreInsumo.data,
                marca=create_form.marca.data,
                unidad=create_form.unidad.data,
                id_proveedor=create_form.id_proveedor.data,
                total=0.0,  # Valor por defecto
            )

            # Añadir a la sesion que tenemos y guardar
            db.session.add(nuevo_insumo)
            db.session.commit()

            flash("Insumo registrado exitosamente", "success")
            return redirect(
                url_for("insumo.insumos")
            )

        elif request.method == "POST":
            flash("Corrige los errores en el formulario", "error")
            print("Errores de validación:", create_form.errors)

    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar insumo: {str(e)}", "error")
        print(f"Error en registrar_insumo: {str(e)}")

    return render_template(
        "Insumos/Insumos_registrar.html",
        form=create_form,
        proveedor_options=proveedor_options,
        tipos_unidad=create_form.unidad.choices,
        active_page="insumos",
    )


#abre lo de la ruta de comprar y guarda en la tabla temporal
@insumo_bp.route("/comprar", methods=["GET", "POST"])
@login_required
@role_required("ADMS", "PROD")
def comprar_insumos():

    UNIDADES = [
        ("Kilogramos", "Kilogramos"),
        ("Gramos", "Gramos"),
        ("Litros", "Litros"),
        ("Mililitros", "Mililitros"),
        ("Unidad", "Unidad"),
    ]

    # proveedores activos
    proveedores_activos = [
        (p.id_proveedor, p.empresa) for p in Proveedor.query.filter_by(estatus=1).all()
    ]

    form = ComprarInsumos(request.form if request.method == "POST" else None)

    form.id_proveedor.choices = proveedores_activos
    form.unidad.choices = UNIDADES

    # validadores originales
    original_validators = {
        "unidad": form.unidad.validators.copy(),
        "cantidad": form.cantidad.validators.copy(),
        "peso": form.peso.validators.copy(),
        "precio": form.precio.validators.copy(),
        "id_insumo": form.id_insumo.validators.copy(),
    }

    # carrito de compras
    if "compras" not in session:
        session["compras"] = []

    # Recuperar proveedor e insumo si vienen en el get
    proveedor_id = request.args.get('proveedor_id')
    insumo_id = request.args.get('insumo_id')
    
    if proveedor_id:
        form.id_proveedor.data = proveedor_id
        # Cargar insumos proveedor 
        form.id_insumo.choices = [
            (i.id_insumo, i.nombreInsumo)
            for i in Insumos.query.filter_by(id_proveedor=proveedor_id)
            .order_by(Insumos.nombreInsumo)
            .all()
        ]
        if insumo_id:
            form.id_insumo.data = insumo_id

    if request.method == "POST":
        # Cargar insumos del proveedor seleccionado
        if form.id_proveedor.data:
            form.id_insumo.choices = [
                (i.id_insumo, i.nombreInsumo)
                for i in Insumos.query.filter_by(id_proveedor=form.id_proveedor.data)
                .order_by(Insumos.nombreInsumo)
                .all()
            ]

        if "filtrar_proveedor" in request.form:
            # Desactivar validaciines
            form.unidad.validators = []
            form.cantidad.validators = []
            form.peso.validators = []
            form.precio.validators = []
            form.id_insumo.validators = []

            # Validar proveedor
            if form.id_proveedor.validate(form):
                flash("Insumos del proveedor cargados", "info")
                # Restaurar opciones del proveedor
                form.id_proveedor.choices = proveedores_activos

        elif "guardar_compra" in request.form:
            # Restaurar validadores
            form.unidad.validators = original_validators["unidad"]
            form.cantidad.validators = original_validators["cantidad"]
            form.peso.validators = original_validators["peso"]
            form.precio.validators = original_validators["precio"]
            form.id_insumo.validators = original_validators["id_insumo"]

            if form.validate():

                proveedor = Proveedor.query.get(form.id_proveedor.data)
                insumo = Insumos.query.get(form.id_insumo.data)
                unidad = form.unidad.data
                peso = float(form.peso.data)
                cantidad = float(form.cantidad.data)
                precio = float(form.precio.data)

                # Conversiones de unidades
                if unidad == "Kilogramos":
                    peso_total = (peso * 1000) * cantidad
                    unidad_almacen = "Gramos"
                elif unidad == "Litros":
                    peso_total = (peso * 1000) * cantidad
                    unidad_almacen = "Mililitros"
                else:
                    peso_total = peso * cantidad
                    unidad_almacen = unidad

                precio_total = cantidad * precio

                # Crear objeto compra
                compra = {
                    "proveedor": proveedor.empresa,
                    "proveedor_id": proveedor.id_proveedor,
                    "id_insumo": insumo.id_insumo,
                    "insumo": insumo.nombreInsumo,
                    "unidad_original": unidad,
                    "peso": peso,
                    "cantidad": cantidad,
                    "peso_total": peso_total,
                    "unidad_almacen": unidad_almacen,
                    "precio_unitario": precio,
                    "precio_total": precio_total,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                # Agregar sesion
                session["compras"].append(compra)
                session.modified = True
                flash("Compra agregada correctamente", "success")
                
                # Guardar valores proveedor e insumo
                proveedor_id = form.id_proveedor.data
                insumo_id = form.id_insumo.data
                
                # Limpiar campos especificos
                form.cantidad.data = ''
                form.peso.data = ''
                form.precio.data = ''
                
                # Recargar pagina manteniendo proveedor e insumo
                return redirect(url_for('insumo.comprar_insumos', 
                                    proveedor_id=proveedor_id, 
                                    insumo_id=insumo_id))
            else:
                flash("Corrige los errores en el formulario", "danger")

        elif "comprar" in request.form:
            if not session["compras"]:
                flash("No hay compras para procesar", "warning")
            else:
                try:
                    # Registrar compra principal
                    nueva_compra = ComprasRealizadas(
                        id_proveedor=session["compras"][0]["proveedor_id"],
                        precio=sum(item["precio_total"] for item in session["compras"]),
                        fecha=datetime.now().date(),
                        numeroOrden=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        estatus=0,
                    )
                    db.session.add(nueva_compra)
                    db.session.flush()

                    # Registrar detalles y lotes
                    for item in session["compras"]:
                        # Detalle de compra
                        detalle = DetalleCompra(
                            descripcion={
                                "id_insumo": item["id_insumo"],
                                "insumo": item["insumo"],
                                "peso": item["peso_total"],
                                "unidad": item["unidad_almacen"],
                                "cantidad": item["cantidad"],
                                "precio_unitario": item["precio_unitario"],
                                "precio_total": item["precio_total"],
                            },
                            compra_id=nueva_compra.id_comprasRealizadas,
                        )
                        db.session.add(detalle)

                        # Nuevo lote
                        nuevo_lote = LoteInsumo(
                            id_insumo=item["id_insumo"],
                            fechaIngreso=datetime.now().date(),
                            fechaCaducidad=datetime.now().date() + timedelta(days=365),
                            cantidad=item["peso_total"],
                            costo=item["precio_unitario"],
                        )
                        db.session.add(nuevo_lote)

                        # Actualizar stock
                        insumo = Insumos.query.get(item["id_insumo"])
                        insumo.total += item["peso_total"]

                    db.session.commit()
                    session["compras"] = []
                    flash("Compra registrada exitosamente", "success")
                    return redirect(url_for("insumo.comprar_insumos"))

                except Exception as e:
                    db.session.rollback()
                    flash(f"Error al registrar compra: {str(e)}", "danger")

    # Restaurar validadores antes de renderizar
    form.unidad.validators = original_validators["unidad"]
    form.cantidad.validators = original_validators["cantidad"]
    form.peso.validators = original_validators["peso"]
    form.precio.validators = original_validators["precio"]
    form.id_insumo.validators = original_validators["id_insumo"]

    return render_template(
        "Insumos/Insumos_comprar.html",
        form=form,
        compras=session["compras"],
        unidades=UNIDADES,
        active_page="insumos",
    )

#guarda lo de la tabla temporal en la base de datos
@insumo_bp.route("/comprar/lista", methods=["GET", "POST"])
@login_required
@role_required("ADMS", "PROD")
def insumos_comprar():

    form = ComprarInsumos(request.form if request.method == "POST" else None)

    UNIDADES = [
        ("Kilogramos", "Kilogramos"),
        ("Gramos", "Gramos"),
        ("Litros", "Litros"),
        ("Mililitros", "Mililitros"),
        ("Unidad", "Unidad"),
    ]
    form.unidad.choices = UNIDADES

    # Cargar proveedor
    form.id_proveedor.choices = [
        (p.id_proveedor, p.empresa) for p in Proveedor.query.filter_by(estatus=1).all()
    ]

    # Inicializar carrito de compras
    if "compras" not in session:
        session["compras"] = []

    if request.method == "POST":

        form = ComprarInsumos(request.form)
        form.unidad.choices = UNIDADES

        # Filtrar insumo por proveedor
        if "filtrar_proveedor" in request.form:
            if form.id_proveedor.validate(form):
                insumos = Insumos.query.filter_by(
                    id_proveedor=form.id_proveedor.data
                ).all()
                form.id_insumo.choices = [
                    (i.id_insumo, i.nombreInsumo) for i in insumos
                ]
                flash("Insumos del proveedor cargados", "info")

        # Agregar al carrito
        elif "guardar_compra" in request.form and form.validate():
            try:
                proveedor = Proveedor.query.get(form.id_proveedor.data)
                insumo = Insumos.query.get(form.id_insumo.data)
                cantidad = float(form.cantidad.data)
                precio_unitario = float(form.precio.data)
                peso = float(form.peso.data)

                # Conversion
                if form.unidad.data == "Kilogramos":
                    peso_total = peso * 1000
                elif form.unidad.data == "Litros":
                    peso_total = peso * 1000
                else:
                    peso_total = peso

                precio_total = cantidad * precio_unitario

                # Agregar compra al carrito
                compra = {
                    "id_insumo": insumo.id_insumo,
                    "insumo": insumo.nombreInsumo,
                    "proveedor_id": proveedor.id_proveedor,
                    "cantidad": cantidad,
                    "peso_total": peso_total,
                    "precio_unitario": precio_unitario,
                    "precio_total": precio_total,
                }

                session["compras"].append(compra)
                session.modified = True
                flash(f"{insumo.nombreInsumo} agregado al carrito", "success")

            except Exception as e:
                flash(f"Error al procesar la compra: {str(e)}", "danger")

        # Procesar compra final
        elif "comprar" in request.form:
            if not session["compras"]:
                flash("No hay compras para procesar", "warning")
            else:
                try:
                    # Registrar compra principal
                    nueva_compra = ComprasRealizadas(
                        id_proveedor=session["compras"][0]["proveedor_id"],
                        precio=sum(item["precio_total"] for item in session["compras"]),
                        fecha=datetime.now().date(),
                        numeroOrden=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        estatus=0,
                    )
                    db.session.add(nueva_compra)
                    db.session.flush()

                    # Registrar detalles
                    for item in session["compras"]:
                        detalle = DetalleCompra(
                            descripcion={
                                "id_insumo": item["id_insumo"],
                                "nombre": item["insumo"],
                                "cantidad": item["cantidad"],
                                "peso_total": item["peso_total"],
                                "precio_unitario": item["precio_unitario"],
                                "precio_total": item["precio_total"],
                            },
                            compra_id=nueva_compra.id_comprasRealizadas,
                        )
                        db.session.add(detalle)

                    db.session.commit()
                    session["compras"] = []
                    flash("Compra registrada exitosamente", "success")
                    return redirect(url_for("insumo.insumos_comprar"))

                except Exception as e:
                    db.session.rollback()
                    flash(f"Error al registrar compra: {str(e)}", "danger")

    return render_template(
        "Insumos/Insumos_comprar.html",
        form=form,
        compras=session["compras"],
        active_page="insumos",
    )

#ruta para limpiar el formulario de compra
@insumo_bp.route("/comprar/limpiar", methods=["GET", "POST"])
@login_required
@role_required("ADMS", "PROD")
def limpiar_compras():
    # Limpiar la lista
    if "compras" in session:
        session.pop("compras")
    flash("Lista de compras limpiada correctamente", "success")
    return redirect(url_for("insumo.comprar_insumos"))

#ruta que elimina el insumo a comprar de la tabla temporal
@insumo_bp.route("/comprar/eliminar/<int:index>", methods=["POST"])
@login_required
@role_required("ADMS", "PROD")
def eliminar_compra(index):
    if "compras" in session:
        if 0 <= index < len(session["compras"]):
            session["compras"].pop(index)
            session.modified = True
            flash("Compra eliminada correctamente", "success")
    return redirect(url_for("insumo.comprar_insumos"))

#abre la ruta y busca el orden de compra para que se vea la tabla con lo que se compro
@insumo_bp.route("/comprados", methods=["GET", "POST"])
@insumo_bp.route("/comprados/<numero_orden>", methods=["GET"])
@login_required
@role_required("ADMS", "PROD")  # Nueva ruta para recibir el número de orden
def comprados_insumos(numero_orden=None):
    form = OrdenCompraForm(request.form if request.method == "POST" else None)
    
    # Si viene número de orden por URL (GET)
    if numero_orden:
        form.numero_orden.data = numero_orden  # Autocompletar el formulario
        return procesar_busqueda_orden(form)
    
    # Si es POST (búsqueda manual)
    if request.method == "POST":
        return procesar_busqueda_orden(form)
    
    # GET sin parámetros (formulario vacío)
    return render_template(
        "Insumos/Insumos_comprados.html",
        form=form,
        active_page="insumos"
    )

@login_required
@role_required("ADMS", "PROD")
def procesar_busqueda_orden(form):
    """Función auxiliar para procesar la búsqueda de órdenes"""
    if not form.validate():
        return render_template(
            "Insumos/Insumos_comprados.html",
            form=form,
            active_page="insumos"
        )

    numero_orden = form.numero_orden.data

    compra = ComprasRealizadas.query.filter_by(numeroOrden=numero_orden).first()

    if not compra:
        flash("No se encontró ninguna orden con ese número", "danger")
        return redirect(url_for("insumo.comprados_insumos"))

    detalles = DetalleCompra.query.filter_by(
        compra_id=compra.id_comprasRealizadas
    ).all()

    detalles_compra = [detalle.descripcion for detalle in detalles]

    dynamic_form = DynamicFechaCaducidadForm.create_form(len(detalles_compra))

    return render_template(
        "Insumos/Insumos_comprados.html",
        form=form,
        dynamic_form=dynamic_form,
        detalles_compra=detalles_compra,
        numero_orden=numero_orden,
        hoy=datetime.now().strftime("%Y-%m-%d"),
        active_page="insumos",
    )

#ruta para registrar y modificar los insumos que se compraron
@insumo_bp.route("/registrar-compra", methods=["POST"])
@login_required
@role_required("ADMS", "PROD")
def registrar_insumos():
    numero_orden = request.form.get("numero_orden")

    if not numero_orden:
        flash("Número de orden no proporcionado", "danger")
        return redirect(url_for("insumo.comprados_insumos"))

    try:
        compra = ComprasRealizadas.query.filter_by(numeroOrden=numero_orden).first()

        if not compra:
            flash("No se encontró la orden especificada", "danger")
            return redirect(url_for("insumo.comprados_insumos"))

        if compra.estatus == 1:
            flash("Esta orden ya fue registrada anteriormente", "warning")
            return redirect(url_for("insumo.comprados_insumos"))

        detalles = DetalleCompra.query.filter_by(
            compra_id=compra.id_comprasRealizadas
        ).all()

        if not detalles:
            flash("No hay insumos para registrar en esta orden", "warning")
            return redirect(url_for("insumo.comprados_insumos"))

        # Procesar cada insumo
        for i, detalle in enumerate(detalles, start=1):
            descripcion = detalle.descripcion
            fecha_caducidad = request.form.get(f"fecha_caducidad_{i}")

            if not fecha_caducidad:
                flash(
                    f"Debe especificar fecha de caducidad para {descripcion['nombre']}",
                    "danger",
                )
                return redirect(url_for("insumo.comprados_insumos"))

            nuevo_lote = LoteInsumo(
                id_insumo=descripcion["id_insumo"],
                fechaIngreso=datetime.now().date(),
                fechaCaducidad=datetime.strptime(fecha_caducidad, "%Y-%m-%d").date(),
                cantidad=descripcion["peso_total"],
                costo=descripcion["precio_unitario"],
            )
            db.session.add(nuevo_lote)

            insumo = Insumos.query.get(descripcion["id_insumo"])
            if insumo:
                insumo.total += descripcion["peso_total"]
            else:
                flash(
                    f"Insumo {descripcion['nombre']} no encontrado en inventario",
                    "danger",
                )
                return redirect(url_for("insumo.comprados_insumos"))

        compra.estatus = 1
        compra.fecha = datetime.now().date()
        db.session.commit()
        flash(
            "Insumos registrados correctamente y orden marcada como recibida", "success"
        )

        # Cambiar para redirigir pag. principal
        return redirect(url_for("insumo.insumos"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar insumos: {str(e)}", "danger")
        return redirect(url_for("insumo.comprados_insumos"))

#abre la ruta de merma dependiendo del id del insumo que esta en la tabla
@insumo_bp.route("/merma/registrar/<int:id_insumo>", methods=["GET", "POST"])
@login_required
@role_required("ADMS", "PROD")
def registrar_merma_insumo(id_insumo):

    insumo = Insumos.query.get_or_404(id_insumo)

    form = InsumosMerma(request.form) if request.method == "POST" else InsumosMerma()

    lotes = LoteInsumo.query.filter(
        LoteInsumo.id_insumo == id_insumo,
        LoteInsumo.cantidad > 0
    ).all()
    
    # si no esta validado
    if not lotes:
        flash("No hay lotes disponibles con existencia para este insumo", "warning")
        return redirect(url_for("insumo.insumos"))

    form.id_lote.choices = [
        (lote.idLote, f"Lote {lote.idLote} - {lote.fechaIngreso.strftime('%Y-%m-%d')} (Disponible: {lote.cantidad} {insumo.unidad})")
        for lote in lotes
    ]

    if request.method == "POST":
        if form.validate():
            try:
                lote = LoteInsumo.query.get(form.id_lote.data)

                if float(form.cantidad.data) > lote.cantidad:
                    flash("La cantidad excede el stock disponible", "danger")
                    return redirect(
                        url_for("insumo.registrar_merma_insumo", id_insumo=id_insumo)
                    )

                merma = MermasInsumos(
                    lote_id=form.id_lote.data,
                    cantidad=float(form.cantidad.data),
                    tipo_merma=form.tipo.data,
                    descripcion=form.descripcion.data,
                    fecha=datetime.now().date(),
                )

                # actualializar stock
                lote.cantidad -= float(form.cantidad.data)
                insumo.total -= float(form.cantidad.data)

                db.session.add(merma)
                db.session.commit()

                flash("Merma registrada exitosamente", "success")
                return redirect(url_for("insumo.insumos"))

            except ValueError:
                db.session.rollback()
                flash("Error: La cantidad debe ser un numero valido", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Error al registrar la merma: {str(e)}", "danger")
        else:
            flash("Por favor corrija los errores en el formulario", "warning")

    return render_template(
        "Insumos/Insumos_merma.html", 
        form=form, 
        insumo=insumo, 
        active_page="insumos"
    )

#borrar insumo permanentemente
@insumo_bp.route("/eliminar/<int:id_insumo>")
@login_required
@role_required("ADMS", "PROD")
def eliminar_insumo(id_insumo):
    try:
        insumo = Insumos.query.get_or_404(id_insumo)
        nombre_insumo = insumo.nombreInsumo
        
        # primero los lotes
        LoteInsumo.query.filter_by(id_insumo=id_insumo).delete()
        
        # luego insumos
        db.session.delete(insumo)
        db.session.commit()
        
        flash(f"Insumo '{nombre_insumo}' eliminado permanentemente con sus lotes asociados", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar insumo: {str(e)}", "error")
        print(f"Error en eliminar_insumo: {str(e)}")
    
    return redirect(url_for("insumo.insumos"))