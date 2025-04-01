from extensions import db

class SolicitudProduccion(db.Model):
    __tablename__ = 'solicitudProduccion'
    
    idSolicitud = db.Column(db.Integer, primary_key=True, autoincrement=True, name='idSolicitud')
    detalleorden_id = db.Column(db.Integer, db.ForeignKey('detalleVentaOrden.id_detalleVentaOrden'), nullable=False)
    fechaCaducidad = db.Column(db.Date, nullable=False)
    estatus = db.Column(db.Integer, nullable=False)  # 0: INACTIVO, 1: TERMINADAS, 2: ENTREGADAS, 3: LOTE
    
    # Relacion
    detalle_orden = db.relationship('DetalleVentaOrden', backref='solicitudes_produccion', lazy=True)