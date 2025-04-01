from extensions import db

class Receta(db.Model):

    _tablename_ = 'receta'

    idReceta = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    nombreReceta = db.Column(db.String(50), nullable=False)
    ingredientes = db.Column(db.JSON, nullable=False)
    Descripccion = db.Column(db.Text)
    estatus = db.Column(db.Integer, default=1)
    cantidad_galletas = db.Column(db.Integer, nullable=False)
    
    # Relacion
    galletas = db.relationship('Galleta', backref='receta', lazy=True)
