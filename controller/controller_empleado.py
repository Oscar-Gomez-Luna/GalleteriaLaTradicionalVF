from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from forms.empleado_form import EmpleadoForm, EmpleadoFormMod
from model.persona import Persona
from model.usuario import Usuario
from model.empleado import Empleado 
from datetime import datetime
from extensions import db

usuario_bp = Blueprint('usuario', __name__, template_folder='../view/', url_prefix='/usuario')

rol_etiquetas = {
    'ADMI': 'Administrador',
    'CAJA': 'Cajero',
    'PROD': 'Producción'
}

@usuario_bp.route("/")
@usuario_bp.route("/catálago")
def empleados():
    mostrar_inactivos = request.args.get('mostrar_inactivos') == 'on'

    if mostrar_inactivos:
        empleados = Empleado.query.join(Persona).join(Usuario).filter(Usuario.estatus == 0).all()
    else:
        empleados = Empleado.query.join(Persona).join(Usuario).filter(Usuario.estatus == 1).all()

    return render_template("administracion/usuarios/usuarios.html", active_page="administracion", active_page_admin="usuarios", empleados=empleados)

@usuario_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_empleado():
    empleado_class = EmpleadoForm(request.form)

    if request.method == 'POST' and empleado_class.validate():
        try:
            ap_paterno = empleado_class.apPaterno.data[:2].upper()
            ap_materno = empleado_class.apMaterno.data[:2].upper()
            nombre = empleado_class.nombre.data[:2].upper()
            fecha_registro = datetime.now()
            dia_mes = fecha_registro.strftime('%d%m')
            rol = empleado_class.rol.data.upper()
            puesto = rol_etiquetas.get(rol, 'Desconocido')

            nombre_usuario = f"{ap_paterno}{ap_materno}{nombre}{dia_mes}{rol}"
            contrasenia = f"{ap_paterno}{ap_materno}{nombre}{dia_mes}{rol}"

            contrasenia_hash = generate_password_hash(contrasenia)

            persona = Persona(
                apPaterno=empleado_class.apPaterno.data,
                apMaterno=empleado_class.apMaterno.data,
                nombre=empleado_class.nombre.data,
                genero=empleado_class.genero.data,
                telefono=empleado_class.telefono.data,
                email=empleado_class.email.data,
                calle=empleado_class.calle.data,
                numero=empleado_class.numero.data,
                colonia=empleado_class.colonia.data,
                codigoPostal=empleado_class.codigoPostal.data,
                fechaNacimiento=empleado_class.fechaNacimiento.data
            )
            db.session.add(persona)
            db.session.commit()
            ultimo_id_persona = persona.idPersona

            usuario = Usuario(
                nombreUsuario=nombre_usuario,
                contrasenia=contrasenia_hash,
                estatus=1,
                rol=empleado_class.rol.data
            )
            db.session.add(usuario)
            db.session.commit()
            ultimo_id_usuario = usuario.idUsuario

            empleado = Empleado(
                puesto=puesto,
                curp=empleado_class.curp.data,
                rfc=empleado_class.rfc.data,
                salarioBruto=empleado_class.salarioBruto.data,
                fechaIngreso=empleado_class.fechaIngreso.data,
                idPersona=ultimo_id_persona,
                idUsuario=ultimo_id_usuario
            )
            db.session.add(empleado)
            db.session.commit()

            flash('Empleado registrado correctamente.', 'success')
            return redirect(url_for('administracion.usuario.empleados'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el empleado', 'danger')

    return render_template("administracion/usuarios/registrar_usuarios.html", active_page="administracion", active_page_admin="usuarios", form=empleado_class)

@usuario_bp.route("/modificar", methods=['GET', 'POST'])
def modificar_empleado():
    idEmpleado = request.args.get('idEmpleado')

    if idEmpleado:
        empleado_class = EmpleadoFormMod(request.form)
        empleado = (
            db.session.query(Empleado)
            .options(db.joinedload(Empleado.persona), db.joinedload(Empleado.usuario))
            .filter(Empleado.idEmpleado == idEmpleado)
            .first())
        
        if not empleado:
            flash("Empleado no encontrado", "danger")
            return redirect(url_for('administracion.usuario.empleados'))
        
        if request.method == 'GET':
            if empleado:
                empleado_class.nombre.data = empleado.persona.nombre
                empleado_class.apPaterno.data = empleado.persona.apPaterno
                empleado_class.apMaterno.data = empleado.persona.apMaterno
                empleado_class.genero.data = empleado.persona.genero
                empleado_class.telefono.data = empleado.persona.telefono
                empleado_class.email.data = empleado.persona.email
                empleado_class.calle.data = empleado.persona.calle
                empleado_class.numero.data = empleado.persona.numero
                empleado_class.colonia.data = empleado.persona.colonia
                empleado_class.codigoPostal.data = empleado.persona.codigoPostal
                empleado_class.fechaNacimiento.data = empleado.persona.fechaNacimiento
                empleado_class.nombreUsuario.data = empleado.usuario.nombreUsuario
                empleado_class.rol.data = empleado.usuario.rol
                empleado_class.curp.data = empleado.curp
                empleado_class.rfc.data = empleado.rfc
                empleado_class.salarioBruto.data = empleado.salarioBruto
                empleado_class.fechaIngreso.data = empleado.fechaIngreso

        if request.method == 'POST' and empleado_class.validate():
            empleado.persona.apPaterno = empleado_class.apPaterno.data
            empleado.persona.apMaterno = empleado_class.apMaterno.data
            empleado.persona.nombre = empleado_class.nombre.data
            empleado.persona.genero = empleado_class.genero.data
            empleado.persona.telefono = empleado_class.telefono.data
            empleado.persona.calle = empleado_class.calle.data
            empleado.persona.numero = empleado_class.numero.data
            empleado.persona.colonia = empleado_class.colonia.data
            empleado.persona.codigoPostal = empleado_class.codigoPostal.data
            empleado.persona.email = empleado_class.email.data
            empleado.persona.fechaNacimiento = empleado_class.fechaNacimiento.data

            empleado.usuario.nombreUsuario = empleado_class.nombreUsuario.data

            nueva_contrasenia = empleado_class.contrasenia.data
            if nueva_contrasenia:
                empleado.usuario.contrasenia = generate_password_hash(nueva_contrasenia)

            empleado.usuario.rol = empleado_class.rol.data

            puesto = rol_etiquetas.get(empleado_class.rol.data, 'Desconocido')

            empleado.puesto = puesto
            empleado.curp = empleado_class.curp.data
            empleado.rfc = empleado_class.rfc.data
            empleado.salarioBruto = empleado_class.salarioBruto.data
            empleado.fechaIngreso = empleado_class.fechaIngreso.data

            db.session.commit()

            flash("Empleado actualizado correctamente", "success")
            return redirect(url_for('administracion.usuario.empleados'))

        return render_template("administracion/usuarios/modificar_usuarios.html", active_page="administracion", active_page_admin="usuarios", form=empleado_class)
    
    else:
        flash("Empleado no encontrado", "danger")
        return redirect(url_for('administracion.usuario.empleados'))

@usuario_bp.route("/detalles", methods=['GET', 'POST'])
def detalles_empleado():
    if request.method == 'GET':
        idEmpleado = request.args.get('idEmpleado')
        empleado = (
            db.session.query(Empleado)
            .options(db.joinedload(Empleado.persona), db.joinedload(Empleado.usuario))
            .filter(Empleado.idEmpleado == idEmpleado)
            .first()
        )

    return render_template("administracion/usuarios/detalle_usuarios.html", active_page="administracion", active_page_admin="usuarios", empleado=empleado)

@usuario_bp.route('/eliminar', methods=['GET', 'POST'])
def eliminar_empleado():
    if request.method == 'GET':
        idEmpleado = request.args.get('idEmpleado') 
        empleado = (
            db.session.query(Empleado)
            .options(db.joinedload(Empleado.persona), db.joinedload(Empleado.usuario))
            .filter(Empleado.idEmpleado == idEmpleado)
            .first()
        )

        if empleado:
            try:
                if empleado.usuario.estatus == 1:
                    empleado.usuario.estatus = 0 
                    db.session.commit() 
                    flash('Empleado eliminado correctamente.', 'success')
                else:
                    flash('El empleado ya está eliminado.', 'warning')
            except Exception as e:
                db.session.rollback()
                flash('Error al eliminar el empleado.', 'danger')
                print(f"Error: {e}")
        else:
            flash('Empleado no encontrado.', 'danger')

        return redirect(url_for('administracion.usuario.empleados'))

    return redirect(url_for('administracion.usuario.empleados'))

@usuario_bp.route('/reactivar', methods=['GET', 'POST'])
def reactivar_empleado():
    if request.method == 'GET':
        idEmpleado = request.args.get('idEmpleado') 
        empleado = (
            db.session.query(Empleado)
            .options(db.joinedload(Empleado.persona), db.joinedload(Empleado.usuario))
            .filter(Empleado.idEmpleado == idEmpleado)
            .first()
        )

        if empleado:
            try:
                if empleado.usuario.estatus == 0:
                    empleado.usuario.estatus = 1 
                    db.session.commit() 
                    flash('Empleado reactivado correctamente.', 'success')
                else:
                    flash('El empleado ya está reactivado.', 'warning')
            except Exception as e:
                db.session.rollback()
                flash('Error al reactivar el empleado.', 'danger')
        else:
            flash('Empleado no encontrado.', 'danger')

        return redirect(url_for('administracion.usuario.empleados'))

    return redirect(url_for('administracion.usuario.empleados'))
