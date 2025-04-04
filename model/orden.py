from extensions import db
from model.cliente import Cliente
from datetime import datetime

class Orden(db.Model):
    __tablename__ = 'orden'

    id_orden = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.Text)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fechaAlta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fechaEntrega = db.Column(db.DateTime, nullable=False)
    tipoVenta = db.Column(db.String(50), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.idCliente'), nullable=False)

    detalles = db.relationship('DetalleVentaOrden', backref='orden_relacion', lazy=True)  # Cambié el backref a 'orden_relacion'
