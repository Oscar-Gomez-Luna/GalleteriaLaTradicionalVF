from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField, DateField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange




# Formulario para registrar lotes de galletas (Producción)
class LoteGalletasForm(FlaskForm):
    galleta_id = SelectField('Galleta', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad Producida', validators=[DataRequired(), NumberRange(min=1)])
    fechaProduccion = DateField('Fecha de Producción', format='%Y-%m-%d', validators=[DataRequired()])
    fechaCaducidad = DateField('Fecha de Caducidad', format='%Y-%m-%d', validators=[DataRequired()])
    costo = DecimalField('Costo de Producción', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    existencia = IntegerField('Existencia', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Registrar Producción')


class EliminarLoteForm(FlaskForm):
    lote_id = IntegerField('ID del lote', validators=[DataRequired()])
    galleta_nombre = StringField('Nombre Galleta')  # opcional solo para mostrar en mensaje flash
    submit = SubmitField('Eliminar')


# Formulario para registrar receta
class RecetaForm(FlaskForm):
    nombreReceta = StringField('Nombre de la Receta', validators=[DataRequired(), Length(min=3, max=50)])
    ingredientes = TextAreaField('Ingredientes (JSON)', validators=[DataRequired()])
    Descripccion = TextAreaField('Descripción del Proceso')
    cantidad_galletas = IntegerField('Cantidad de Galletas', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Registrar Receta')


# Formulario para registrar merma de galletas
class MermaGalletaForm(FlaskForm):
    lote_id = SelectField('Lote de Galleta', coerce=int, validators=[DataRequired()])
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


# Formulario para registrar merma de insumos
class MermaInsumoForm(FlaskForm):
    insumo_id = SelectField('Insumo', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad a Descontar', validators=[DataRequired(), NumberRange(min=1)])
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