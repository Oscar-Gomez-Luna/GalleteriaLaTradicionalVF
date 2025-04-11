from wtforms import Form, HiddenField, StringField, TextAreaField
from wtforms import (
    SelectField,
    DecimalField,
)
from wtforms import validators

class MermaGalletaform(Form):
    
    id_galleta = HiddenField(
        "Galleta ID",
        validators=[validators.DataRequired()]
    )
    id_lote = SelectField(
        "Lote",
        [validators.DataRequired(message="Seleccione un lote")],
        choices=[],
        coerce=int,
        render_kw={"disabled": True}
    )
    tipo_merma = SelectField(
    "Tipo de merma",
    [validators.DataRequired(message="Seleccione tipo de merma")],
    choices=[
        ('Durante produccion', 'Durante produccion'),
        ('Por caducidad', 'Por caducidad'),
        ('Por almacenamiento', 'Por almacenamiento'),
        ('Por manipulacion', 'Por manipulacion'),
        ('Otro', 'Otro')
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