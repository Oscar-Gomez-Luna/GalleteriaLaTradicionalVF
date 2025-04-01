from extensions import db

class CorteCaja(db.Model):
    __tablename__ = 'corte_caja'
    
    id_ganancia = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    fecha = db.Column(db.Date, nullable=False)
    totalVenta = db.Column(db.Float, nullable=False)
    cantidadCaja = db.Column(db.Numeric(10, 2), nullable=False)               
    diferencial = db.Column(db.Numeric(10, 2), nullable=False)
    observaciones = db.Column(db.String(200))