from extensions import db

from extensions import db

class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    idCliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPersona = db.Column(db.Integer, db.ForeignKey('persona.idPersona', ondelete='CASCADE'), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario', ondelete='CASCADE'), nullable=False)
    
    usuario = db.relationship('Usuario', back_populates='cliente')
