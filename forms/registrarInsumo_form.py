from wtforms import Form, TextAreaField
from wtforms import (
    StringField,
    PasswordField,
    EmailField,
    BooleanField,
    IntegerField,
    SubmitField,
    DateField,
    SelectField,
    DecimalField,
)
from wtforms import validators

class RegistrarInsumo(Form):
    nombreInsumo = StringField(
        "Nombre del Insumo",
        [
            validators.DataRequired(message="El nombre es requerido"),
            validators.Length(min=2, max=20, message="Requiere min=3 max=20"),
        ],
    )

    marca = StringField(
        "Marca",
        [
            validators.DataRequired(message="La marca es requerida"),
            validators.Length(min=2, max=20, message="Requiere min=3 max=20"),
        ],
    )

    unidad = SelectField(
        "Unidad",
        [validators.DataRequired(message="La unidad es requerida")],
        choices=[],
    )  # las asigno dinamicamente

    id_proveedor = SelectField(
        "Proveedor",
        [validators.DataRequired(message="El proveedor es requerido")],
        choices=[],
        coerce=int,
    ) 
