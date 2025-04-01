from extensions import db
from sqlalchemy.dialects.mysql import LONGTEXT

class Usuario(db.Model):
    __tablename__ = 'usuario'
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreUsuario = db.Column(db.String(20), unique=True, nullable=False)
    token = db.Column(db.String(255))
    estatus = db.Column(db.Integer, nullable=False, default=1)
    contrasenia = db.Column(LONGTEXT, nullable=False)
    rol = db.Column(db.String(4), nullable=False)
    ultima_conexion = db.Column(db.DateTime)