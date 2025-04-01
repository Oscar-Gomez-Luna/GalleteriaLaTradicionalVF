from extensions import db

# Tabla receta
class Receta(db.Model):
    __tablename__ = 'receta'
    idReceta = db.Column(db.Integer, primary_key=True)
    nombreReceta = db.Column(db.String(50), nullable=False)
    ingredientes = db.Column(db.JSON, nullable=False)
    Descripccion = db.Column(db.Text)
    estatus = db.Column(db.Integer, default=1)
    cantidad_galletas = db.Column(db.Integer)

    galletas = db.relationship('Galleta', backref='receta', lazy=True)