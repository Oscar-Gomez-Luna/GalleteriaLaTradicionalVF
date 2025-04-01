from extensions import db
from model.lote_galleta import LoteGalletas

class MermaGalletas(db.Model):
    __tablename__ = 'mermasGalletas'

    id_merma = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotesGalletas.id_lote'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    tipo_merma = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text)

    # Relación con el modelo LoteGalletas
    lote = db.relationship('LoteGalletas', backref=db.backref('mermasGalletas', lazy=True))
