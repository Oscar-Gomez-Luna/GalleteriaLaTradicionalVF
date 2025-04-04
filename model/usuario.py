from extensions import db
from flask_login import UserMixin
import datetime
from sqlalchemy.dialects.mysql import LONGTEXT
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreUsuario = db.Column(db.String(20), unique=True, nullable=False)
    token = db.Column(db.String(255))
    estatus = db.Column(db.Integer, nullable=False, default=1)
    contrasenia = db.Column(db.Text, nullable=False)
    rol = db.Column(db.String(4), nullable=False)
    ultima_conexion = db.Column(db.DateTime)

    clientes = db.relationship('Cliente', backref='usuario_cliente', lazy=True)
    verificacion = db.relationship('VerificacionUsuario', backref='usuario', uselist=False, lazy=True)
    seguridad = db.relationship('UsuarioSeguridad', backref='usuario', uselist=False, lazy=True)


    def set_password(self, password):
        """Encripta la contraseña y la almacena."""
        self.contrasenia = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con la almacenada."""
        return check_password_hash(self.contrasenia, password)

    def get_id(self):
        return str(self.idUsuario)

    @property
    def is_active(self):
        return self.estatus == 1

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __repr__(self):
        return f'<Usuario {self.nombreUsuario}>'