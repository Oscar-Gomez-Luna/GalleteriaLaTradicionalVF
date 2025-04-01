from wtforms import Form, StringField, DateField
from wtforms.validators import DataRequired

class OrdenCompraForm(Form):
    numero_orden = StringField(
        "Número de Orden",
        validators=[DataRequired(message="El número de orden es requerido")]
    )

class DynamicFechaCaducidadForm:
    """Clase para crear formularios dinámicos con campos de fecha"""
    @staticmethod
    def create_form(num_campos):
        """Crea un formulario con campos de fecha dinámicos"""
        class FechaCaducidadForm(Form):
            pass

        for i in range(1, num_campos + 1):
            setattr(
                FechaCaducidadForm,
                f"fecha_caducidad_{i}",
                DateField(
                    "Fecha Caducidad",
                    validators=[DataRequired(message="La fecha de caducidad es requerida")],
                    format="%Y-%m-%d"
                )
            )
        
        return FechaCaducidadForm()