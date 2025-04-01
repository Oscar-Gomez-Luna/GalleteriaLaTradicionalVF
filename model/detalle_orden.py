from extensions import db

class DetalleVentaOrden(db.Model):
    __tablename__ = 'detalleVentaOrden'

    id_detalleVentaOrden = db.Column(db.Integer, primary_key=True)
    galletas_id = db.Column(db.Integer, db.ForeignKey('galletas.id_galleta'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id_orden'), nullable=False)

    # Relaciones
    galleta = db.relationship('Galleta', backref=db.backref('detalles_venta', lazy=True))