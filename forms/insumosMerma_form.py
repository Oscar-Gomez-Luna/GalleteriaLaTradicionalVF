from wtforms import Form, TextAreaField
from wtforms import (
    StringField,
    SelectField,
    DecimalField,
)
from wtforms import validators

class InsumosMerma(Form):
    id_lote = SelectField(
        "Lote",
        [validators.DataRequired(message="Seleccione un lote")],
        choices=[],
        coerce=int
    )
    tipo = SelectField(
    "Tipo de merma",
    [validators.DataRequired(message="Seleccione tipo de merma")],
    choices=[
        ('Desperdiciado', 'Desperdiciado'),
        ('Por caducidad', 'Por caducidad'),
        ('Producto dañado', 'Producto dañado')
    ],
    render_kw={"class": "form-select"}
)
    cantidad = DecimalField(
        "Cantidad",
        [
            validators.DataRequired(message="Ingrese la cantidad"),
            validators.NumberRange(min=0.01, message="La cantidad debe ser mayor a 0")
        ],
        places=2
    )
    descripcion = TextAreaField(
        "Descripción",
        [validators.Optional()]
    )
