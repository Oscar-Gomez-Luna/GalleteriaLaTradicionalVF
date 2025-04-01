from extensions import db

class MermasInsumos(db.Model):
    __tablename__ = 'mermasInsumos'
    
    id_merma = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('loteinsumo.idLote'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    tipo_merma = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha = db.Column(db.Date, nullable=False)

    #Relacion loteInsumo
    lote = db.relationship('LoteInsumo', backref=db.backref('mermas', lazy=True))
