from wtforms import Form
from wtforms import (
    SelectField,
    DecimalField,
)
from wtforms import validators


class ComprarInsumos(Form):
    id_proveedor = SelectField(
        "Proveedor",
        [validators.DataRequired(message="El proveedor es requerido")],
        choices=[],
        coerce=int,
    )

    id_insumo = SelectField(
        "Insumo",
        [validators.DataRequired(message="El insumo es requerido")],
        choices=[],
        coerce=int,
    )

    cantidad = DecimalField(
        "Cantidad",
        [validators.DataRequired(message="La cantidad es requerida")],
    )

    peso = DecimalField(
        "Peso",
        [validators.DataRequired(message="El peso es requerido")],
    )

    precio = DecimalField(
        "Precio",
        [validators.DataRequired(message="El precio es requerido")],
    )

    unidad = SelectField(
        "Unidad",
        [validators.DataRequired(message="La unidad es requerida")],
        choices=[],
    )
