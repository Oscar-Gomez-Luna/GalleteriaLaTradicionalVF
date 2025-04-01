from extensions import db

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    
    id_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa = db.Column(db.String(100), nullable=False)
    fechaRegistro = db.Column(db.Date, nullable=False)
    estatus = db.Column(db.Integer, nullable=False, default=1)
    calle = db.Column(db.String(50), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    colonia = db.Column(db.String(50), nullable=False)
    codigoPostal = db.Column(db.Integer, nullable=False)
    telefono = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    rfc = db.Column(db.String(12), nullable=False)


    # Relacion tabla Insumos
    insumos = db.relationship('Insumos', backref='proveedor', lazy=True)
