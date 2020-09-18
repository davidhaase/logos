from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SourceTxtForm(FlaskForm):
    form_input = StringField('Enter text to translate', validators=[DataRequired()])
    submit = SubmitField('Submit')
