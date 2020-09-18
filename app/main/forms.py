from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField('Enter text to translate', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SourceTxtForm(FlaskForm):
    form_input = TextAreaField('Enter text to translate', validators=[DataRequired()])
    submit = SubmitField('Submit')
