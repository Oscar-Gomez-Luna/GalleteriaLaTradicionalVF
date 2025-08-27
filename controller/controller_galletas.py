from flask import Blueprint, render_template, request, flash, redirect, url_for
from model.galleta import db, Galleta
from model.tipo_galleta import TipoGalleta 
from model.lote_galleta import LoteGalletas
from model.merma_galleta import MermaGalleta
from model.receta import Receta
from flask_login import current_user
from forms.galleta_forms import MermaGalletaForm
from sqlalchemy import func
from flask_login import login_required
from extensions import role_required

galletas_bp = Blueprint('galletas', __name__, url_prefix="/galletas")

def obtener_galletas_unidad_con_existencia():
    subq = db.session.query(
        LoteGalletas.galleta_id,
        func.sum(LoteGalletas.existencia).label("total")
    ).group_by(LoteGalletas.galleta_id).subquery()

    return db.session.query(Galleta)\
        .join(TipoGalleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta)\
        .join(subq, Galleta.id_galleta == subq.c.galleta_id)\
        .filter(TipoGalleta.nombre == "Unidad")\
        .filter(subq.c.total > 0)\
        .all()
 
@galletas_bp.route("/", methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "PROD", "CAJA")
def galletas():
    from forms.galleta_forms import NuevaGalletaForm
    nueva_form = NuevaGalletaForm()
    mostrar_modal = False
    merma_form = MermaGalletaForm()

    # Mostrar modal
    if request.method == 'POST' and 'abrir_modal_galleta' in request.form:
        mostrar_modal = True

    recetas = Receta.query.filter_by(estatus=1).all()
    nueva_form.receta_id.choices = [(r.idReceta, r.nombreReceta) for r in recetas]

    galletas_con_existencia = obtener_galletas_unidad_con_existencia()
    merma_form.galleta_id.choices = [(g.id_galleta, g.galleta) for g in galletas_con_existencia]

    subquery = db.session.query(
        LoteGalletas.galleta_id,
        func.sum(LoteGalletas.existencia).label("total_existencia")
    ).group_by(LoteGalletas.galleta_id).subquery()

    unidad_base = db.session.query(
        Galleta.id_galleta,
        Galleta.galleta.label("nombre_galleta"),
        TipoGalleta.costo,
        func.coalesce(subquery.c.total_existencia, 0).label("existencia")
    ).join(TipoGalleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta)\
     .outerjoin(subquery, Galleta.id_galleta == subquery.c.galleta_id)\
     .filter(TipoGalleta.nombre == "Unidad").all()

    galletas_unidad = []
    galletas_caja_kilo = []
    galletas_caja_medio_kilo = []

    for g in unidad_base:
        galletas_unidad.append({
            'nombre_galleta': g.nombre_galleta,
            'tipo_empaquetado': 'Unidad',
            'costo': g.costo,
            'existencia': g.existencia
        })
    # Consultar existencia "Caja de Kilo"
    caja_kilo = db.session.query(
        Galleta.galleta.label("nombre_galleta"),
        TipoGalleta.costo,
        Galleta.existencia
    ).join(TipoGalleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta)\
    .filter(TipoGalleta.nombre == "Caja de Kilo")\
    .filter(Galleta.existencia > 0)\
    .all()

    for g in caja_kilo:
        galletas_caja_kilo.append({
            'nombre_galleta': g.nombre_galleta,
            'tipo_empaquetado': 'Caja de Kilo',
            'costo': g.costo,
            'existencia': g.existencia
        })

    # 700 gramos:
    caja_700 = db.session.query(
        Galleta.galleta.label("nombre_galleta"),
        TipoGalleta.costo,
        Galleta.existencia
    ).join(TipoGalleta, Galleta.tipo_galleta_id == TipoGalleta.id_tipo_galleta)\
    .filter(TipoGalleta.nombre == "Caja de 700 gramos")\
    .filter(Galleta.existencia > 0)\
    .all()

    for g in caja_700:
        galletas_caja_medio_kilo.append({
            'nombre_galleta': g.nombre_galleta,
            'tipo_empaquetado': 'Caja de 700 gramos',
            'costo': g.costo,
            'existencia': g.existencia
        })




    return render_template(
        "galleta/galletas.html",
        nueva_form=nueva_form,
        mostrar_modal=mostrar_modal,
        merma_form=merma_form,
        galletas_unidad=galletas_unidad,
        galletas_caja_kilo=galletas_caja_kilo,
        galletas_caja_medio_kilo=galletas_caja_medio_kilo,
        galletas=galletas_con_existencia,
        active_page="galletas",
        usuario = current_user
    )


@galletas_bp.route("/agregar-galleta", methods=["POST"])
@login_required
@role_required("ADMS", "PROD", "CAJA")
def agregar_galleta():
    from forms.galleta_forms import NuevaGalletaForm
    form = NuevaGalletaForm()
    form.receta_id.choices = [(r.idReceta, r.nombreReceta) for r in Receta.query.filter_by(estatus=1).all()]

    if form.validate_on_submit():
        nombre = form.nombre_galleta.data
        receta_id = form.receta_id.data

        tipos = TipoGalleta.query.all()
        for tipo in tipos:
            nueva = Galleta(
                tipo_galleta_id=tipo.id_tipo_galleta,
                galleta=nombre,
                existencia=0,
                receta_id=receta_id
            )
            db.session.add(nueva)
        db.session.commit()
        flash("Galleta creada en sus tres presentaciones", "success")

    return redirect(url_for("galletas.galletas"))


@galletas_bp.route("/merma-galleta", methods=["POST"])
@login_required
@role_required("ADMS", "PROD", "CAJA")
def merma_galleta():
    form = MermaGalletaForm()

    galletas_con_existencia = obtener_galletas_unidad_con_existencia()
    form.galleta_id.choices = [(g.id_galleta, g.galleta) for g in galletas_con_existencia]

    if form.validate_on_submit():
        galleta_id = form.galleta_id.data
        cantidad = form.cantidad.data

        lote = LoteGalletas.query\
            .filter_by(galleta_id=galleta_id)\
            .filter(LoteGalletas.existencia > 0)\
            .order_by(LoteGalletas.fechaProduccion.asc())\
            .first()

        if not lote:
            flash("No hay lotes disponibles con existencia para esta galleta.", "warning")
            return redirect(url_for("galletas.galletas"))

        if cantidad > lote.existencia:
            flash(f"La cantidad solicitada ({cantidad}) excede la existencia del lote ({lote.existencia}).", "danger")
            return redirect(url_for("galletas.galletas"))

        lote.existencia -= cantidad

        nueva_merma = MermaGalleta(
            tipo_merma=form.tipo_merma.data,
            lote_id=lote.id_lote,
            cantidad=cantidad,
            descripcion=form.descripcion.data,
            fecha=form.fecha.data
        )
        db.session.add(nueva_merma)
        db.session.commit()

        flash("Merma registrada correctamente.", "success")
    else:
        flash("Por favor completa todos los campos correctamente.", "danger")

    return redirect(url_for("galletas.galletas"))
