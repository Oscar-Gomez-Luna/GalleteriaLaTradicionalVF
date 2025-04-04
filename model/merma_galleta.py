from extensions import db

# Tabla mermasGalletas
class MermaGalleta(db.Model):
    __tablename__ = 'mermasGalletas'
    __table_args__ = {'extend_existing': True} 
    
    id_merma = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotesGalletas.id_lote'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    tipo_merma = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text)

    lote = db.relationship('LoteGalletas', backref='mermas', lazy=True)