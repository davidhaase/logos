from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class TranslationForm(FlaskForm):    
    form_input_lang_selection = SelectField('Choose a source language', validators=[DataRequired()])
    form_output_lang_selection = SelectField('Choose an target language', validators=[DataRequired()])
    form_input = StringField('Enter text to translate', validators=[DataRequired()])
    submit = SubmitField('Submit')
