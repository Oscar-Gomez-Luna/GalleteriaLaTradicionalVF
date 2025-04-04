from extensions import db

class Persona(db.Model):
    __tablename__ = 'persona'
    idPersona = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genero = db.Column(db.String(1), nullable=False, default="O")
    apPaterno = db.Column(db.String(20), nullable=False)
    apMaterno = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(10), nullable=False)
    calle = db.Column(db.String(50), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    colonia = db.Column(db.String(50), nullable=False)
    codigoPostal = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    fechaNacimiento = db.Column(db.Date, nullable=False)

    # Relación con Cliente
    clientes = db.relationship('Cliente', backref='persona_cliente', lazy=True)
    
    # Relación con Empleado
    empleados = db.relationship('Empleado', backref='persona_empleado', lazy=True)

    def __repr__(self):
        return f'<Persona {self.nombre}>'
