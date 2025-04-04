from extensions import db
from model.persona import Persona
from model.usuario import Usuario 

class Empleado(db.Model):
    __tablename__ = 'empleado'
    idEmpleado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    puesto = db.Column(db.String(45), nullable=False)
    curp = db.Column(db.String(18), nullable=False)
    rfc = db.Column(db.String(13), nullable=False)
    salarioBruto = db.Column(db.Float, nullable=False)
    fechaIngreso = db.Column(db.Date, nullable=False)
    idPersona = db.Column(db.Integer, db.ForeignKey('persona.idPersona'), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    persona = db.relationship('Persona', backref=db.backref('empleados_relacionados', cascade='all, delete-orphan'))
    usuario = db.relationship('Usuario', backref=db.backref('empleados', cascade='all, delete-orphan'))
