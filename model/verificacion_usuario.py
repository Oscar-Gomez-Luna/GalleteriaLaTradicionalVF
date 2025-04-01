# model/verificacion_usuario.py
from extensions import db
import datetime

class VerificacionUsuario(db.Model):
    __tablename__ = 'verificacion_usuario'
    
    idVerificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)
    verificado = db.Column(db.Boolean, nullable=False, default=False)
    codigo_verificacion = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f'<VerificacionUsuario {self.idVerificacion}>'