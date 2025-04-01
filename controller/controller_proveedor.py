from flask import Blueprint, render_template, request, flash, redirect, url_for
from model.proveedor import Proveedor
from forms.proveedor_form import ProveedorForm
from extensions import db

proovedor_bp = Blueprint('proveedor', __name__, template_folder='../view/', url_prefix='/proveedor')

@proovedor_bp.route("/")
@proovedor_bp.route("/catálago")
def proveedores():
    mostrar_inactivos = request.args.get('mostrar_inactivos') == 'on'

    if mostrar_inactivos:
        proveedores = Proveedor.query.filter(Proveedor.estatus == 0).all()
    else:
        proveedores =  Proveedor.query.filter(Proveedor.estatus == 1).all()

    return render_template("administracion/proveedores/proveedores.html", active_page="administracion", active_page_admin="proveedores", proveedores=proveedores)

@proovedor_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_proveedor():
    proveedor_class = ProveedorForm(request.form)

    if request.method == 'POST' and proveedor_class.validate():
        try:
            proveedor = Proveedor(
                empresa=proveedor_class.empresa.data,
                fechaRegistro=proveedor_class.fechaRegistro.data,
                estatus = 1,
                calle=proveedor_class.calle.data,
                numero=proveedor_class.numero.data,
                colonia=proveedor_class.colonia.data,
                codigoPostal=proveedor_class.codigoPostal.data,
                telefono=proveedor_class.telefono.data,
                email=proveedor_class.email.data,
                rfc=proveedor_class.rfc.data
            )
            db.session.add(proveedor)
            db.session.commit()
            
            flash('Proovedor registrado correctamente.', 'success')
            return redirect(url_for('administracion.proveedor.proveedores'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el proveedor', 'danger')

    return render_template("administracion/proveedores/registrar_proveedores.html", active_page="administracion", active_page_admin="proveedores", form=proveedor_class)

@proovedor_bp.route("/modificar", methods=['GET', 'POST'])
def modificar_proveedor():
    idProveedor = request.args.get('idProveedor')

    if idProveedor:
        proveedor_class = ProveedorForm(request.form)
        proveedor = (
            db.session.query(Proveedor).filter(Proveedor.id_proveedor == idProveedor).first())
        
        if not proveedor:
            flash("¨Proveedor no encontrado", "danger")
            return redirect(url_for('administracion.proveedor.proveedores'))
        
        if request.method == 'GET':
            if proveedor:
                proveedor_class.empresa.data = proveedor.empresa
                proveedor_class.fechaRegistro.data = proveedor.fechaRegistro
                proveedor_class.calle.data = proveedor.calle
                proveedor_class.numero.data = proveedor.numero
                proveedor_class.colonia.data = proveedor.colonia
                proveedor_class.codigoPostal.data = proveedor.codigoPostal
                proveedor_class.telefono.data = proveedor.telefono
                proveedor_class.email.data = proveedor.email
                proveedor_class.rfc.data = proveedor.rfc

        if request.method == 'POST' and proveedor_class.validate():
            proveedor.empresa = proveedor_class.empresa.data
            proveedor.fechaRegistro = proveedor_class.fechaRegistro.data
            proveedor.calle = proveedor_class.calle.data
            proveedor.numero = proveedor_class.numero.data
            proveedor.colonia = proveedor_class.colonia.data
            proveedor.codigoPostal = proveedor_class.codigoPostal.data
            proveedor.telefono = proveedor_class.telefono.data
            proveedor.email = proveedor_class.email.data
            proveedor.rfc = proveedor_class.rfc.data

            db.session.commit()

            flash("Proveedor actualizado correctamente", "success")
            return redirect(url_for('administracion.proveedor.proveedores'))

        return render_template("administracion/proveedores/modificar_proveedores.html", active_page="administracion", active_page_admin="proveedores",form=proveedor_class)
    
    else:
        flash("proveedor no encontrado", "danger")
        return redirect(url_for('administracion.proveedor.proveedores'))

@proovedor_bp.route("/detalles", methods=['GET', 'POST'])
def detalles_proveedor():
    if request.method == 'GET':
        idProveedor = request.args.get('idProveedor')
        proveedor = (
            db.session.query(Proveedor).filter(Proveedor.id_proveedor == idProveedor).first()
        )

    return render_template("administracion/proveedores/detalle_proveedores.html", active_page="administracion", active_page_admin="proveedores", proveedor=proveedor)

@proovedor_bp.route('/eliminar', methods=['GET', 'POST'])
def eliminar_proveedor():
    if request.method == 'GET':
        idProveedor = request.args.get('idProveedor') 
        proveedor = (
            db.session.query(Proveedor).filter(Proveedor.id_proveedor == idProveedor).first())

        if proveedor:
            try:
                if proveedor.estatus == 1:
                    proveedor.estatus = 0 
                    db.session.commit() 
                    flash('Proovedor eliminado correctamente.', 'success')
                else:
                    flash('El proveedor ya está eliminado.', 'warning')
            except Exception as e:
                db.session.rollback()
                flash('Error al eliminar el proveedor.', 'danger')
                print(f"Error: {e}")
        else:
            flash('Proovedor no encontrado.', 'danger')

        return redirect(url_for('administracion.proveedor.proveedores'))

    return redirect(url_for('administracion.proveedor.proveedores'))

@proovedor_bp.route('/reactivar', methods=['GET', 'POST'])
def reactivar_proveedor():
    if request.method == 'GET':
        idProveedor = request.args.get('idProveedor') 
        proveedor = (
            db.session.query(Proveedor).filter(Proveedor.id_proveedor == idProveedor).first())

        if proveedor:
            try:
                if proveedor.estatus == 0:
                    proveedor.estatus = 1 
                    db.session.commit() 
                    flash('Proovedor reactivado correctamente.', 'success')
                else:
                    flash('El proveedor ya está activo.', 'warning')
            except Exception as e:
                db.session.rollback()
                flash('Error al reactivar el proveedor.', 'danger')
        else:
            flash('Proveedor no encontrado.', 'danger')

        return redirect(url_for('administracion.proveedor.proveedores'))

    return redirect(url_for('administracion.proveedor.proveedores'))