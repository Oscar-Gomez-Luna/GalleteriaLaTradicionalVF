from extensions import db

class Galleta(db.Model):
    __tablename__ = 'galletas'

    id_galleta = db.Column(db.Integer, primary_key=True)
    tipo_galleta_id = db.Column(db.Integer, db.ForeignKey('tipo_galleta.id_tipo_galleta'), nullable=False)
    galleta = db.Column(db.String(100), nullable=False)
    existencia = db.Column(db.Integer, nullable=False)
    receta_id = db.Column(db.Integer, db.ForeignKey('receta.idReceta'), nullable=False)

    # Relación con receta
    receta = db.relationship('Receta', backref=db.backref('galletas', lazy=True))