from extensions import db

class DetalleCompra(db.Model):
    __tablename__ = 'detalleCompra'

    id_detalleCompra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.JSON, nullable=False)
    compra_id = db.Column(db.Integer, db.ForeignKey('comprasRealizadas.id_comprasRealizadas'), nullable=False)
    
    # Relacion
    compra = db.relationship('ComprasRealizadas', backref=db.backref('detallesCompra', lazy=True))
    