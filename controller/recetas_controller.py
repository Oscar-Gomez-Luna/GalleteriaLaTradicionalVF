from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from model.receta import db, Receta
from forms.forms import RecetaForm
from flask_login import login_required, current_user
from extensions import role_required
import os
from werkzeug.utils import secure_filename
from datetime import datetime

recetas_bp = Blueprint('recetas', __name__, url_prefix='/recetas', template_folder='view')

# Configuración para imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/img/galletas'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file):
    if file and file.filename != '' and allowed_file(file.filename):
        # Asegurar que el directorio existe
        os.makedirs(os.path.join(current_app.root_path, UPLOAD_FOLDER), exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
        
        # Guardar el archivo
        file.save(filepath)
        return filename
    return None

@recetas_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required("ADMS") 
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
                         active_page_admin="recetas",
                         usuario=current_user)

@recetas_bp.route('/agregar', methods=['GET', 'POST'])
@login_required
@role_required("ADMS") 
def agregar():
    receta_form = RecetaForm(request.form)
    
    if request.method == 'POST' and receta_form.validate():
        # Procesar imagen
        imagen_file = request.files.get('imagen_galleta')
        imagen_nombre = save_uploaded_image(imagen_file) if imagen_file else None
        
        # Si no se subió imagen o hubo error, usar default.png
        if not imagen_nombre:
            imagen_nombre = 'default.png'
            flash("No se subió una imagen válida, se usará la imagen por defecto", "info")
        
        # Resto del código para crear la receta...
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
            estatus=1,
            imagen_galleta=imagen_nombre
        )
        
        db.session.add(nueva_receta)
        try:
            db.session.commit()
            flash("Receta agregada correctamente", "success")
            return redirect(url_for('administracion.recetas.recetas'))
        except Exception as e:
            db.session.rollback()
            # Eliminar la imagen si hubo error al guardar
            if imagen_nombre and imagen_nombre != 'default.png':
                try:
                    os.remove(os.path.join(current_app.root_path, UPLOAD_FOLDER, imagen_nombre))
                except:
                    pass
            flash(f"Error al guardar la receta: {str(e)}", "danger")

    return render_template('administracion/recetas/agregar_receta.html', form=receta_form)

@recetas_bp.route('/modificar', methods=['GET', 'POST'])
@login_required
@role_required("ADMS") 
def modificar():
    idReceta = request.args.get('idReceta')
    if not idReceta:
        flash("Receta no encontrada", "danger")
        return redirect(url_for('recetas.recetas'))

    receta = Receta.query.get_or_404(idReceta)
    receta_form = RecetaForm(obj=receta)
    receta_form.descripcion.data = receta.Descripccion

    if request.method == 'POST' and receta_form.validate():
        # Manejo de la imagen
        imagen_file = request.files.get('imagen_galleta')
        nueva_imagen = None
        
        # Verificar si se subió una nueva imagen
        if imagen_file and imagen_file.filename != '':
            nueva_imagen = save_uploaded_image(imagen_file)
            if nueva_imagen:
                # Eliminar la imagen anterior si existe y no es default.png
                if receta.imagen_galleta and receta.imagen_galleta != 'default.png':
                    try:
                        old_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, receta.imagen_galleta)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception as e:
                        flash(f"No se pudo eliminar la imagen anterior: {str(e)}", "warning")
                
                receta.imagen_galleta = nueva_imagen
            else:
                flash("La imagen subida no es válida, se mantendrá la actual", "warning")

        # Actualizar otros campos
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

        try:
            db.session.commit()
            flash("Receta actualizada correctamente", "success")
            return redirect(url_for('administracion.recetas.recetas'))
        except Exception as e:
            db.session.rollback()
            # Si hubo error, eliminar la nueva imagen si se subió
            if nueva_imagen:
                try:
                    os.remove(os.path.join(current_app.root_path, UPLOAD_FOLDER, nueva_imagen))
                except:
                    pass
            flash(f"Error al actualizar la receta: {str(e)}", "danger")

    return render_template('administracion/recetas/modificar_receta.html', 
                         form=receta_form, 
                         idReceta=idReceta, 
                         receta=receta,
                         active_page="administracion",
                         active_page_admin="recetas", 
                         usuario=current_user)