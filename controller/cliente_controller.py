from flask import Blueprint, render_template, request, redirect, url_for, flash
from model.cliente import db, Cliente
from model.persona import db,  Persona
from model.usuario import db, Usuario
from forms.forms import ClienteForm

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes', template_folder='view')

@clientes_bp.route('/', methods=['GET'])
def clientes():
    mostrar_inactivos = request.args.get('inactivos') == 'on'
    
    query = Cliente.query.join(Persona).join(Usuario)
     
    if mostrar_inactivos:
        query = query.filter(Usuario.estatus == 0)
    else:
        query = query.filter(Usuario.estatus == 1)
    
    clientes = query.all()
    return render_template('administracion/clientes/clientes.html', 
                         clientes=clientes,
                         mostrar_inactivos=mostrar_inactivos, active_page="administracion", active_page_admin="clientes")


@clientes_bp.route('/modificar', methods=['GET', 'POST'])
def modificar_cliente():
    idCliente = request.args.get('idCliente')
    cliente = Cliente.query.filter_by(idCliente=idCliente).first()

    if not cliente:
        flash("Cliente no encontrado", "danger")
        return redirect(url_for('administracion.clientes.clientes'))

    persona = Persona.query.filter_by(idPersona=cliente.idPersona).first()

    cliente_form = ClienteForm(obj=cliente)

    if request.method == 'POST' and cliente_form.validate():
        # Actualizar datos de Persona
        persona.nombre = cliente_form.persona.nombre.data
        persona.apPaterno = cliente_form.persona.apPaterno.data
        persona.apMaterno = cliente_form.persona.apMaterno.data
        persona.genero = cliente_form.persona.genero.data
        persona.telefono = cliente_form.persona.telefono.data
        persona.calle = cliente_form.persona.calle.data
        persona.numero = cliente_form.persona.numero.data
        persona.colonia = cliente_form.persona.colonia.data
        persona.codigoPostal = cliente_form.persona.codigoPostal.data
        persona.email = cliente_form.persona.email.data
        persona.fechaNacimiento = cliente_form.persona.fechaNacimiento.data


        # Guardar cambios en la BD
        db.session.add(persona)
        db.session.commit()

        flash("Cliente actualizado correctamente", "success")
        return redirect(url_for('administracion.clientes.clientes'))

    return render_template('administracion/clientes/modificar_cliente.html', form=cliente_form, idCliente=idCliente, active_page="administracion", active_page_admin="clientes")



@clientes_bp.route('/eliminar', methods=['GET'])
def eliminar_cliente():
    idCliente = request.args.get('idCliente')
    usuario = Usuario.query.filter_by(idUsuario=idCliente).first()

    if usuario:
        usuario.estatus = 0 
        db.session.commit()
        flash("Cliente desactivado correctamente", "success")
    else:
        flash("Cliente no encontrado", "danger")

    return redirect(url_for('administracion.clientes.clientes'))

@clientes_bp.route('/activar', methods=['GET'])
def activar_cliente():
    idCliente = request.args.get('idCliente')
    usuario = Usuario.query.filter_by(idUsuario=idCliente).first()

    if usuario:
        usuario.estatus = 1 
        db.session.commit()
        flash("Cliente activado correctamente", "success")
    else:
        flash("Cliente no encontrado", "danger")

    return redirect(url_for('administracion.clientes.clientes'))

@clientes_bp.route('/detalles', methods=['GET'])
def detalles_clientes():
    idCliente = request.args.get('idCliente')
    cliente = Cliente.query.filter_by(idCliente=idCliente).first()
    return render_template("administracion/clientes/detalle_cliente.html",cliente=cliente, active_page="administracion", active_page_admin="clientes")
