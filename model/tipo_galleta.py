# model/tipo_galleta.py
from extensions import db

class TipoGalleta(db.Model):
    __tablename__ = 'tipo_galleta'

    id_tipo_galleta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f'<TipoGalleta {self.nombre}>'