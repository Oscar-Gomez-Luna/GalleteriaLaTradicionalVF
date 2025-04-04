from extensions import db
from model.galleta import Galleta
from model.orden import Orden

class DetalleVentaOrden(db.Model):
    __tablename__ = 'detalleVentaOrden'

    id_detalleVentaOrden = db.Column(db.Integer, primary_key=True, autoincrement=True)
    galletas_id = db.Column(db.Integer, db.ForeignKey('galletas.id_galleta'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id_orden'), nullable=False)

    # Relación con el modelo Orden
    orden = db.relationship('model.orden.Orden', backref=db.backref('detalle_venta_orden', lazy=True))

    # Relación con el modelo Galletas
    galletas = db.relationship('model.galleta.Galleta', backref=db.backref('detalleVentaOrdenGalleta', lazy=True))
