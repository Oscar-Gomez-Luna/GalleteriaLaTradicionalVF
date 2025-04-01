from extensions import db

class Insumos(db.Model):
    __tablename__ = 'insumos'
    id_insumo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreInsumo = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(30), nullable=False)
    unidad = db.Column(db.String(50), nullable=False)
    total = db.Column(db.Float, nullable=False)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedor.id_proveedor'), nullable=False)

    # Relacion LoteInsumo
    lotes = db.relationship('LoteInsumo', backref='insumo', lazy=True)