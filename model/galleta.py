from extensions import db
from model.tipo_galleta import TipoGalleta
from model.receta import Receta

class Galleta(db.Model):
    __tablename__ = 'galletas'
    
    id_galleta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_galleta_id = db.Column(db.Integer, db.ForeignKey('tipo_galleta.id_tipo_galleta'), nullable=False)
    galleta = db.Column(db.String(100), nullable=False)
    existencia = db.Column(db.Integer, nullable=False)
    receta_id = db.Column(db.Integer, db.ForeignKey('receta.idReceta'), nullable=False)
    
    # Relación con receta
    receta = db.relationship('Receta', backref=db.backref('galletas', lazy=True))  # Este backref permanece igual
    detalles_venta = db.relationship('DetalleVentaOrden', backref='galleta', lazy=True)
    tipo = db.relationship('TipoGalleta', back_populates='galletas')  # Usar back_populates correctamente
    
    # Modificar el backref para la relación con LoteGalletas
    lotes = db.relationship('LoteGalletas', backref='galleta_lotes', lazy=True)  # Cambié 'galleta' a 'galleta_lotes'


    def __repr__(self):
        return f'<Galleta {self.galleta}>'
