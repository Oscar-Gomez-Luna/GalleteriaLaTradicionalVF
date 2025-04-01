from extensions import db

class Cliente(db.Model):
    __tablename__ = 'cliente'
    idCliente = db.Column(db.Integer, primary_key=True)
    idPersona = db.Column(db.Integer, db.ForeignKey('persona.idPersona'), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    persona = db.relationship('Persona', backref=db.backref('clientes', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('clientes', lazy=True))