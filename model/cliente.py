# model/cliente.py
from extensions import db

class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    idCliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPersona = db.Column(db.Integer, db.ForeignKey('persona.idPersona'), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    def __repr__(self):
        return f'<Cliente {self.idCliente}>'