from flask import Blueprint, render_template, redirect, url_for, flash, request
from model.galleta import db, Galleta
from model.lote_galleta import LoteGalletas
from model.receta import Receta
from model.merma_galleta import MermaGalleta
from model.merma_insumo import MermasInsumos
from model.insumo import Insumos
from model.lote_insumo import LoteInsumo
from flask_login import login_required
from extensions import role_required
from sqlalchemy import text
from forms.produccion_forms import LoteGalletasForm, MermaGalletaForm, MermaInsumoForm, EmpaqueForm
import datetime
from datetime import date
from flask_login import current_user
import json
from collections import defaultdict
from flask_wtf.csrf import generate_csrf

produccion_bp = Blueprint('produccion', __name__, url_prefix="/produccion")

@produccion_bp.route('/produccion', methods=['GET', 'POST'])
@login_required
@role_required("ADMS", "PROD") 
def produccion():
    form = LoteGalletasForm()
    merma_form = MermaGalletaForm()
    
    tipo_unidad = db.session.execute(
    text("SELECT id_tipo_galleta FROM tipo_galleta WHERE nombre = 'Unidad'")
    ).scalar()
    merma_insumo_form = MermaInsumoForm()
    merma_insumo_form.insumo_id.choices = [(i.id_insumo, i.nombreInsumo) for i in Insumos.query.all()]
    form_empaque = EmpaqueForm()
    galletas_con_existencia = db.session.execute(text("""
        SELECT 
            g.id_galleta, g.galleta, SUM(l.existencia) as total
        FROM galletas g
        JOIN lotesGalletas l ON g.id_galleta = l.galleta_id
        WHERE g.tipo_galleta_id = (
            SELECT id_tipo_galleta FROM tipo_galleta WHERE nombre = 'Unidad'
        )
        GROUP BY g.id_galleta, g.galleta
        HAVING total > 0
        ORDER BY g.galleta ASC
    """)).mappings().all()

    form_empaque.galleta_id.choices = [
        (g['id_galleta'], f"{g['galleta']} (Total: {g['total']})") for g in galletas_con_existencia
    ]
    


     # opciones para el select
    form.galleta_id.choices = [
        (g.id_galleta, g.galleta) for g in Galleta.query.filter_by(tipo_galleta_id=tipo_unidad).all()
    ]

    merma_form.lote_id.choices = [(l.id_lote, f"{l.galleta.galleta} | {l.fechaProduccion}") for l in LoteGalletas.query.order_by(LoteGalletas.fechaProduccion.desc()).all()]


    mostrar_modal = False
    mostrar_modal_merma = False
    galleta_seleccionada = None
    fecha_hoy = date.today()
    galleta_id = None  

    mostrar_modal_empaque = request.args.get("abrir_modal_empaque") == "1"
    #Cantidades del los empaques 

    tipo_empaque = request.args.get("tipo_empaque")
    if tipo_empaque:
        form_empaque.tipo_empaque.data = tipo_empaque
        if tipo_empaque == "kilo":
            form_empaque.cantidad_por_empaque.data = 27
        elif tipo_empaque == "700":
            form_empaque.cantidad_por_empaque.data = 20
        else:  # unidad
            form_empaque.cantidad_por_empaque.data = 1

    

 
    # campos de cantidad y costo al seleccionar una galleta
    if request.method == 'GET' and 'galleta_id' in request.args and 'abrir_modal_empaque' not in request.args:
        galleta_id = int(request.args.get('galleta_id'))
        form.galleta_id.data = galleta_id
        mostrar_modal = True


        galleta = Galleta.query.get(galleta_id)
        if galleta and galleta.receta_id:
            receta = Receta.query.get(galleta.receta_id)
            if receta:
                form.cantidad.data = receta.cantidad_galletas
                form.costo.data = receta.cantidad_galletas * 4.5
                form.existencia.data = receta.cantidad_galletas


    lote_merma = None
    if 'merma_lote_id' in request.args:
        mostrar_modal_merma = True
        lote_merma = LoteGalletas.query.get(int(request.args['merma_lote_id']))


    if form.validate_on_submit():
        galleta = Galleta.query.get(form.galleta_id.data)
        receta = Receta.query.get(galleta.receta_id)
        ingredientes = receta.ingredientes
        if isinstance(ingredientes, str):
            ingredientes = json.loads(ingredientes)


        for ingrediente in ingredientes:
            nombre_ingrediente = ingrediente['insumo']
            unidad = ingrediente['unidad']
            cantidad_base = int(ingrediente['cantidad'])

            cantidad_total = cantidad_base * form.cantidad.data // receta.cantidad_galletas

            insumo = db.session.execute(
                text("SELECT * FROM insumos WHERE nombreInsumo = :nombre AND unidad = :unidad"),
                {'nombre': nombre_ingrediente, 'unidad': unidad}
            ).mappings().first()

            if not insumo:
                flash(f"Insumo '{nombre_ingrediente}' con unidad '{unidad}' no encontrado.", 'danger')
                return redirect(url_for('produccion.produccion'))

            lotes = db.session.execute(
                text("SELECT * FROM loteinsumo WHERE id_insumo = :id AND cantidad > 0 ORDER BY fechaIngreso ASC"),
                {'id': insumo['id_insumo']}
            ).mappings().all()

            cantidad_faltante = cantidad_total
            for lote in lotes:
                if cantidad_faltante <= 0:
                    break
                if lote['cantidad'] >= cantidad_faltante:
                    db.session.execute(
                        text("UPDATE loteinsumo SET cantidad = cantidad - :descontar WHERE idLote = :id"),
                        {'descontar': cantidad_faltante, 'id': lote['idLote']}
                    )
                    cantidad_faltante = 0
                else:
                    db.session.execute(
                        text("UPDATE loteinsumo SET cantidad = 0 WHERE idLote = :id"),
                        {'id': lote['idLote']}
                    )
                    cantidad_faltante -= lote['cantidad']

            if cantidad_faltante > 0:
                flash(f"No hay suficiente '{nombre_ingrediente}' para producir {form.cantidad.data} galletas.", 'danger')
                db.session.rollback()
                return redirect(url_for('produccion.produccion'))
            
            db.session.execute(
                text("UPDATE insumos SET total = total - :cantidad WHERE id_insumo = :id"),
                {'cantidad': cantidad_total, 'id': insumo['id_insumo']}
            )

        # Crear lote de galletas
        nueva_fecha_caducidad = form.fechaProduccion.data + datetime.timedelta(days=7)
        nuevo_lote = LoteGalletas(
            galleta_id=form.galleta_id.data,
            fechaProduccion=form.fechaProduccion.data,
            fechaCaducidad=nueva_fecha_caducidad,
            cantidad=form.cantidad.data,
            costo=form.costo.data,
            existencia=form.cantidad.data
        )
        galleta.existencia += form.cantidad.data
        db.session.add(nuevo_lote)
        db.session.commit()
        flash('Producción registrada con éxito.', 'success')
        return redirect(url_for('produccion.produccion'))
    
        # Procesar merma
    if merma_form.validate_on_submit():
        try:
            lote_id = int(request.form.get('lote_id') or merma_form.lote_id.data)
        except (ValueError, TypeError):
            flash("Lote inválido.", 'danger')
            return redirect(url_for('produccion.produccion'))

        lote = LoteGalletas.query.get(lote_id)

        if not lote:
            flash("Lote no encontrado.", 'danger')
            return redirect(url_for('produccion.produccion'))

        cantidad_merma = merma_form.cantidad.data

        if lote.existencia < cantidad_merma:
            flash(f"La cantidad de merma excede la existencia del lote ({lote.existencia}).", 'danger')
            return redirect(url_for('produccion.produccion'))

        nueva_merma = MermaGalleta(
            lote_id=lote.id_lote,
            cantidad=cantidad_merma,
            tipo_merma="En producción",
            fecha=merma_form.fecha.data,
            descripcion=merma_form.descripcion.data
        )

        lote.existencia -= cantidad_merma
        db.session.add(nueva_merma)
        db.session.commit()

        flash(f"Merma registrada correctamente para '{lote.galleta.galleta}'.", 'success')
        return redirect(url_for('produccion.produccion'))

    # Lotes con existencia > 0
    galletas = db.session.execute(text("""
        SELECT 
            lotesGalletas.id_lote,
            galletas.id_galleta,
            galletas.galleta,
            lotesGalletas.existencia,
            receta.nombreReceta,
            lotesGalletas.fechaProduccion,
            lotesGalletas.fechaCaducidad,
            lotesGalletas.cantidad,
            lotesGalletas.costo
        FROM lotesGalletas
        JOIN galletas ON lotesGalletas.galleta_id = galletas.id_galleta
        JOIN receta ON galletas.receta_id = receta.idReceta
        WHERE galletas.tipo_galleta_id = (
            SELECT id_tipo_galleta FROM tipo_galleta WHERE nombre = 'Unidad'
        ) AND lotesGalletas.existencia > 0
        ORDER BY lotesGalletas.fechaProduccion DESC;
    """)).mappings().all()

    alertas_agotamiento = []
    alertas_caducidad = []
    alertas_sin_existencia = []

    # Sumar existencia total por galleta
    galletas_dict = defaultdict(int)
    for lote in galletas:
        galletas_dict[lote['galleta']] += lote['existencia']
        # Alerta: galletas con existencia total en 0
    alertas_sin_existencia = []

    for nombre, total in galletas_dict.items():
        if total == 0:
            alertas_sin_existencia.append(nombre)


    # galletas sin existencia
    todas_las_galletas = db.session.execute(text("""
        SELECT galleta FROM galletas 
        WHERE tipo_galleta_id = (
            SELECT id_tipo_galleta FROM tipo_galleta WHERE nombre = 'Unidad'
        )
    """)).scalars().all()

    for nombre in todas_las_galletas:
        total = galletas_dict.get(nombre, 0)
        if total == 0:
            alertas_sin_existencia.append(nombre)
        elif total <= 30:
            alertas_agotamiento.append({'nombre': nombre, 'total': total})

    # Revisar caducidad solo si hay existencia
    for lote in galletas:
        dias_restantes = (lote['fechaCaducidad'] - fecha_hoy).days
        if dias_restantes <= 3:
            alertas_caducidad.append({
                'nombre': lote['galleta'],
                'existencia': lote['existencia'],
                'dias_restantes': dias_restantes
            })


    return render_template(
        'produccion/produccion.html',
        form=form,
        merma_form=merma_form,
        galletas=galletas,
        fecha_hoy=fecha_hoy.isoformat(),
        fecha_caducidad=(fecha_hoy + datetime.timedelta(days=7)).isoformat(),
        mostrar_modal=mostrar_modal,
        mostrar_modal_merma=mostrar_modal_merma,
        form_empaque=form_empaque,
        galleta_seleccionada=galleta_seleccionada,
        galleta_id=galleta_id,
        lote_merma=lote_merma,alertas_agotamiento=alertas_agotamiento,  
        alertas_caducidad=alertas_caducidad,
        alertas_sin_existencia=alertas_sin_existencia, 
        merma_insumo_form=merma_insumo_form, 
        mostrar_modal_empaque=mostrar_modal_empaque,
        active_page="produccion",
        csrf_token=generate_csrf(),
        usuario = current_user
    )

@produccion_bp.route('/eliminar-lote', methods=['POST'])
@login_required
@role_required("ADMS", "PROD") 
def eliminar_lote():
    lote_id = request.form.get('lote_id')
    galleta_nombre = request.form.get('galleta_nombre')

    if not lote_id:
        flash("No se especificó el lote a eliminar.", "danger")
        return redirect(url_for('produccion.produccion'))

    lote = LoteGalletas.query.get(int(lote_id))

    if not lote:
        flash("Lote no encontrado.", "danger")
        return redirect(url_for('produccion.produccion'))

    MermaGalleta.query.filter_by(lote_id=lote.id_lote).delete()

    db.session.delete(lote)
    db.session.commit()

    flash(f"El lote de la galleta '{galleta_nombre}' ha sido eliminado con éxito.", "success")
    return redirect(url_for('produccion.produccion'))


@produccion_bp.route('/merma-insumo', methods=['POST'])
@login_required
@role_required("ADMS", "PROD") 
def merma_insumo():
    merma_insumo_form = MermaInsumoForm()
     
    # Cargar opciones ANTES de validar
    merma_insumo_form.insumo_id.choices = [(i.id_insumo, i.nombreInsumo) for i in Insumos.query.all()]

    if not merma_insumo_form.validate_on_submit():
        flash("Formulario de merma inválido.", "danger")
        return redirect(url_for('produccion.produccion'))

    insumo_id = merma_insumo_form.insumo_id.data
    cantidad_merma = merma_insumo_form.cantidad.data

    lotes = LoteInsumo.query.filter(LoteInsumo.id_insumo == insumo_id)\
    .filter(LoteInsumo.cantidad > 0)\
    .order_by(LoteInsumo.fechaIngreso.asc()).all()


    cantidad_faltante = cantidad_merma

    for lote in lotes:
        if cantidad_faltante <= 0:
            break

        descontar = min(lote.cantidad, cantidad_faltante)
        lote.cantidad -= descontar

        merma = MermasInsumos(
            lote_id=lote.idLote,
            cantidad=descontar,
            tipo_merma=merma_insumo_form.tipo_merma.data,
            descripcion=merma_insumo_form.descripcion.data,
            fecha=merma_insumo_form.fecha.data
        )
        db.session.add(merma)
        cantidad_faltante -= descontar

    if cantidad_faltante > 0:
        flash("La merma supera la cantidad total disponible en los lotes.", "danger")
        db.session.rollback()
    else:
        insumo = Insumos.query.get(insumo_id)
        if insumo:
            insumo.total -= cantidad_merma
            if insumo.total < 0:
                insumo.total = 0
        db.session.commit()
        flash("Merma registrada correctamente.", "success")

    return redirect(url_for('produccion.produccion'))


@produccion_bp.route('/empaquetar', methods=['POST'])
@login_required
@role_required("ADMS", "PROD")
def empaquetar():
    tipo_empaque = request.form.get("tipo_empaque")  # unidad, kilo, 700
    galleta_id = int(request.form.get("galleta_id") or 0)
    cantidad_por_empaque = int(request.form.get("cantidad_por_empaque") or 0)
    cantidad_empaques = int(request.form.get("cantidad_empaques") or 0)

    # Validación temprana
    if not tipo_empaque or not galleta_id or not cantidad_empaques or not cantidad_por_empaque:
        flash("Faltan datos para empaquetar correctamente.", "danger")
        return redirect(url_for("produccion.produccion"))

    total_galletas_necesarias = cantidad_por_empaque * cantidad_empaques

    # Buscar la galleta original
    galleta = Galleta.query.get(galleta_id)
    if not galleta:
        flash("Galleta no encontrada.", "danger")
        return redirect(url_for("produccion.produccion"))

    # Obtener los lotes disponibles
    lotes = LoteGalletas.query.filter_by(galleta_id=galleta_id)\
        .filter(LoteGalletas.existencia > 0)\
        .order_by(LoteGalletas.fechaProduccion.asc()).all()

    existencia_total = sum([l.existencia for l in lotes])

    if existencia_total < total_galletas_necesarias:
        flash(f"No hay suficientes galletas para empaquetar. Se necesitan {total_galletas_necesarias} y solo hay {existencia_total}.", "danger")
        return redirect(url_for("produccion.produccion"))

    # Descontar existencia
    cantidad_restante = total_galletas_necesarias
    for lote in lotes:
        if cantidad_restante <= 0:
            break
        if lote.existencia >= cantidad_restante:
            lote.existencia -= cantidad_restante
            cantidad_restante = 0
        else:
            cantidad_restante -= lote.existencia
            lote.existencia = 0

    # Mapear tipo_empaque al nombre real
    nombres_tipo = {
        "unidad": "Unidad",
        "kilo": "Caja de Kilo",
        "700": "Caja de 700 gramos"
    }

    tipo_nombre = nombres_tipo.get(tipo_empaque)
    if not tipo_nombre:
        flash("Tipo de empaquetado no válido.", "danger")
        return redirect(url_for("produccion.produccion"))

    tipo_id = db.session.execute(
        text("SELECT id_tipo_galleta FROM tipo_galleta WHERE nombre = :nombre"),
        {"nombre": tipo_nombre}
    ).scalar()

    if not tipo_id:
        flash("Tipo de empaquetado no encontrado en base de datos.", "danger")
        return redirect(url_for("produccion.produccion"))

    # galleta destino del mismo nombre pero otro tipo
    galleta_destino = Galleta.query.filter_by(
        galleta=galleta.galleta,
        tipo_galleta_id=tipo_id
    ).first()

    if not galleta_destino:
        flash(f"No existe un registro para empaquetado tipo '{tipo_nombre}' de la galleta '{galleta.galleta}'.", "danger")
        return redirect(url_for("produccion.produccion"))

    # Sumar empaques producidos
    galleta_destino.existencia += cantidad_empaques
    db.session.commit()

    flash("Empaquetado realizado con éxito.", "success")
    return redirect(url_for("produccion.produccion"))
