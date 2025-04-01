from extensions import db
from model.lote_galleta import LoteGalletas

class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    ticket = db.Column(db.Text)
    tipoVenta = db.Column(db.String(50), nullable=False)
    