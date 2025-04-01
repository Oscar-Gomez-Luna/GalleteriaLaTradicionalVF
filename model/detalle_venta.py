from extensions import db
from model.lote_galleta import LoteGalletas
from model.venta import Venta

class DetalleVentaGalletas(db.Model):
    __tablename__ = 'detalleVentaGalletas'
    
    id_detalleVentaGalletas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id_venta'), nullable=False)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotesGalletas.id_lote'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    venta = db.relationship('Venta', backref=db.backref('detalles', lazy=True))
 
    # Eliminamos la definición explícita de 'venta' porque el backref en Venta ya la crea
    lote = db.relationship('LoteGalletas', backref=db.backref('ventas_detalle', lazy=True))

    def __repr__(self):
        return f'<DetalleVentaGalletas {self.id_detalleVentaGalletas}>'
