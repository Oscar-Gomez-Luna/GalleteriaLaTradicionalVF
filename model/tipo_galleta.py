from extensions import db

class TipoGalleta(db.Model):
    __tablename__ = 'tipo_galleta'    
    id_tipo_galleta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)

    galletas = db.relationship('Galleta', backref='tipo_galleta', lazy=True)
    
    def __repr__(self):
        return f'<TipoGalleta {self.nombre}>'
