from extensions import db

class LoteInsumo(db.Model):
    __tablename__ = 'loteinsumo'
    idLote = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_insumo = db.Column(db.Integer, db.ForeignKey('insumos.id_insumo'), nullable=False)
    fechaIngreso = db.Column(db.Date, nullable=False)
    fechaCaducidad = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)