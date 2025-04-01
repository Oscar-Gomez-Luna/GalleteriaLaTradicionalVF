from extensions import db

class ComprasRealizadas(db.Model):
    __tablename__ = 'comprasRealizadas'
    id_comprasRealizadas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedor.id_proveedor'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    numeroOrden = db.Column(db.String(50), nullable=False)
    estatus = db.Column(db.Integer, nullable=False, default=0)  # 0: En proceso; 1: Llego

    # Relacion provedores
    proveedor = db.relationship('Proveedor', backref='compras_realizadas', lazy=True)