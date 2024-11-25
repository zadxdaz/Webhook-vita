from wtforms import StringField, TextAreaField,SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional

class ClienteForm(FlaskForm):
    nombre_completo = StringField('Nombre Completo', validators=[DataRequired()])
    celular = StringField('Celular', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    ciudad = StringField('Ciudad', validators=[Optional()])  # New field
    comentarios = TextAreaField('Comentarios', validators=[Optional()])  # New field
    submit = SubmitField('Guardar')
