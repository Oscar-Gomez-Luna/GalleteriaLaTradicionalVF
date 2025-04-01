from wtforms import Form, StringField, TextAreaField
from wtforms import (
    SelectField,
    DecimalField,
)
from wtforms import validators

class MermaForm(Form):
    
    id_insumo = SelectField(
        "Insumo",
        [validators.DataRequired(message="El insumo es requerido")],
        choices=[],
        coerce=int,
    )
    id_lote = SelectField(
        "Lote",
        [validators.DataRequired(message="Seleccione un lote")],
        choices=[],
        coerce=int,
        render_kw={"disabled": True}
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