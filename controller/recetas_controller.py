from flask import Blueprint, render_template, request, redirect, url_for, flash
from model.receta import db, Receta
from forms.forms import RecetaForm
import json

recetas_bp = Blueprint('recetas', __name__, url_prefix='/recetas', template_folder='view')

@recetas_bp.route('/', methods=['GET', 'POST'])
def recetas():
    if request.method == 'POST':
        return redirect(url_for('recetas.agregar'))
    
    mostrar_inactivos = 'inactivos' in request.args
    
    query = Receta.query
    if mostrar_inactivos:
        query = query.filter_by(estatus=0)
    else:
        query = query.filter_by(estatus=1)
    
    return render_template('administracion/recetas/recetas.html', 
                         receta=query.all(),
                         mostrar_inactivos=mostrar_inactivos,
                         active_page="administracion",
                         active_page_admin="recetas")

@recetas_bp.route('/agregar', methods=['GET', 'POST'])
def agregar():
    receta_form = RecetaForm(request.form)
    
    if request.method == 'POST' and receta_form.validate():
        nombre = receta_form.nombreReceta.data
        descripcion = receta_form.descripcion.data
        cantidad_galletas = receta_form.cantidad_galletas.data
        insumos = request.form.getlist('insumo[]')
        cantidades = request.form.getlist('cantidad[]')
        unidades = request.form.getlist('unidad[]')
        
        ingredientes = [
            {'insumo': i, 'cantidad': c, 'unidad': u}
            for i, c, u in zip(insumos, cantidades, unidades)
            if i and c and u
        ]
        
        nueva_receta = Receta(
            nombreReceta=nombre,
            Descripccion=descripcion, 
            ingredientes=ingredientes,
            cantidad_galletas=cantidad_galletas,
            estatus=1
        )
        
        db.session.add(nueva_receta)
        db.session.commit()
        
        flash("Receta agregada correctamente", "success")
        return redirect(url_for('administracion.recetas.recetas'))

    return render_template('administracion/recetas/agregar_receta.html', form=receta_form)

@recetas_bp.route('/eliminar', methods=['GET'])
def eliminar():
    idReceta = request.args.get('idReceta')
    receta = Receta.query.filter_by(idReceta=idReceta).first()
    
    if receta:
        receta.estatus = 0
        db.session.commit()
        flash("Receta desactivada correctamente", "success")
    else:
        flash("Receta no encontrada", "danger")

    return redirect(url_for('administracion.recetas.recetas'))

@recetas_bp.route('/activar', methods=['GET'])
def activar():
    idReceta = request.args.get('idReceta')
    receta = Receta.query.filter_by(idReceta=idReceta).first()
    
    if receta:
        receta.estatus = 1
        db.session.commit()
        flash("Receta activada correctamente", "success")
    else:
        flash("Receta no encontrada", "danger")

    return redirect(url_for('administracion.recetas.recetas'))

@recetas_bp.route('/modificar', methods=['GET', 'POST'])
def modificar():
    idReceta = request.args.get('idReceta')
    if not idReceta:
        flash("Receta no encontrada", "danger")
        return redirect(url_for('recetas.recetas'))

    receta = Receta.query.filter_by(idReceta=idReceta).first()
    receta_form = RecetaForm(obj=receta)
    receta_form.descripcion.data = receta.Descripccion

    if not receta:
        flash("Receta no encontrada", "danger")
        return redirect(url_for('administracion.recetas.recetas'))

    if request.method == 'POST' and receta_form.validate():
        receta.nombreReceta = receta_form.nombreReceta.data
        receta.Descripccion = request.form.get('descripcion') 
        receta.cantidad_galletas = receta_form.cantidad_galletas.data

        insumos = request.form.getlist('insumo[]')
        cantidades = request.form.getlist('cantidad[]')
        unidades = request.form.getlist('unidad[]')

        receta.ingredientes = [
            {'insumo': i, 'cantidad': c, 'unidad': u}
            for i, c, u in zip(insumos, cantidades, unidades)
            if i and c and u
        ]

        db.session.commit()
        flash("Receta actualizada correctamente", "success")
        return redirect(url_for('administracion.recetas.recetas'))

    return render_template('administracion/recetas/modificar_receta.html', form=receta_form, idReceta=idReceta, receta=receta, active_page="administracion",
                         active_page_admin="recetas")