from extensions import db

# Tabla mermasInsumos
class MermaInsumo(db.Model):
    __tablename__ = 'mermasInsumos'
    id_merma = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('loteinsumo.idLote'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    tipo_merma = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.Date, nullable=False)

    lote = db.relationship('LoteInsumo', backref='mermas', lazy=True)