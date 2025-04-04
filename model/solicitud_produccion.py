from extensions import db
from model.detalle_venta_orden import DetalleVentaOrden

class SolicitudProduccion(db.Model):
    __tablename__ = 'solicitudProduccion'
    __table_args__ = {'extend_existing': True}

    idSolicitud = db.Column(db.Integer, primary_key=True, autoincrement=True)
    detalleorden_id = db.Column(db.Integer, db.ForeignKey('detalleVentaOrden.id_detalleVentaOrden'), nullable=False)
    fechaCaducidad = db.Column(db.Date, nullable=False)
    estatus = db.Column(db.Integer, nullable=False)

    # Relación con el modelo DetalleVentaOrden
    detalleOrden = db.relationship('DetalleVentaOrden', backref=db.backref('solicitudesProduccion', lazy=True))