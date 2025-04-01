from extensions import db

class TipoGalleta(db.Model):
    _tablename_ = 'tipo_galleta'
    
    id_tipo_galleta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relacion con Galleta
    galletas = db.relationship('Galleta', back_populates='tipo', lazy=True)

