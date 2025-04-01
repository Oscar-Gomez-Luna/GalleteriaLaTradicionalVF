# model/usuario_seguridad.py
from extensions import db
import datetime

class UsuarioSeguridad(db.Model):
    __tablename__ = 'usuario_seguridad'
    
    idUsuarioSeguridad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    password_last_changed = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f'<UsuarioSeguridad {self.idUsuarioSeguridad}>'