from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField, DateField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange



# Formulario para registrar una galleta
class GalletaForm(FlaskForm):
    galleta = StringField('Nombre de la Galleta', validators=[DataRequired(), Length(min=3, max=100)])
    tipo_galleta_id = SelectField('Tipo de Empaquetado', coerce=int, validators=[DataRequired()])
    existencia = IntegerField('Existencia', validators=[DataRequired(), NumberRange(min=0)])
    receta_id = SelectField('Receta', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Registrar Galleta')


# forms.py
class NuevaGalletaForm(FlaskForm):
    receta_id = SelectField('Receta', coerce=int, validators=[DataRequired()])
    nombre_galleta = StringField('Nombre de la Galleta', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Agregar')

# Formulario para tipo de galleta (opcional si lo necesitas)
class TipoGalletaForm(FlaskForm):
    nombre = StringField('Nombre del Tipo', validators=[DataRequired(), Length(min=3, max=50)])
    costo = DecimalField('Costo por Tipo', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    submit = SubmitField('Guardar Tipo')

# Formulario para registrar receta
class RecetaForm(FlaskForm):
    nombreReceta = StringField('Nombre de la Receta', validators=[DataRequired(), Length(min=3, max=50)])
    ingredientes = TextAreaField('Ingredientes (JSON)', validators=[DataRequired()])
    Descripccion = TextAreaField('Descripción del Proceso')
    cantidad_galletas = IntegerField('Cantidad de Galletas', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Registrar Receta')


class MermaGalletaForm(FlaskForm):
    galleta_id = SelectField('Galleta', coerce=int, validators=[DataRequired()])  # NUEVO CAMPO
    lote_id = HiddenField()  # CAMBIO: de SelectField a HiddenField
    cantidad = IntegerField('Cantidad de Merma', validators=[DataRequired(), NumberRange(min=1)])
    tipo_merma = SelectField('Tipo de Merma', choices=[
        ('producción', 'Durante producción'),
        ('almacenamiento', 'Por almacenamiento'),
        ('caducidad', 'Por caducidad'),
        ('manipulacion', 'Por manipulación'),
        ('otro', 'Otro')
    ], validators=[DataRequired()])
    fecha = DateField('Fecha de Merma', format='%Y-%m-%d', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción de la Merma', validators=[Length(max=500)])
    submit = SubmitField('Registrar Merma')