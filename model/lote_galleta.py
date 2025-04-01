# model/lote_galleta.py
from extensions import db
from model.galleta import Galleta

class LoteGalletas(db.Model):
    __tablename__ = 'lotesGalletas'

    id_lote = db.Column(db.Integer, primary_key=True, autoincrement=True)
    galleta_id = db.Column(db.Integer, db.ForeignKey('galletas.id_galleta'), nullable=False)
    fechaProduccion = db.Column(db.Date, nullable=False)
    fechaCaducidad = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)
    existencia = db.Column(db.Integer, nullable=False)

    # Relación con Galleta
    galleta = db.relationship('Galleta', backref=db.backref('lotes', lazy=True))

    def __repr__(self):
        return f'<LoteGalletas {self.id_lote}>'