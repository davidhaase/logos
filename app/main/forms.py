from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class TranslationForm(FlaskForm):    
    form_selection_input_lang = SelectField('Choose a source language', validators=[DataRequired()])
    form_selection_output_lang = SelectField('Choose an target language', validators=[DataRequired()])
    form_string_input = StringField('Enter text to translate', validators=[DataRequired()])
    submit = SubmitField('Submit')

class BuildModelForm(FlaskForm):
    form_selection_input_lang = SelectField('Choose a source language', validators=[DataRequired()])
    form_selection_output_lang = SelectField('Choose an target language', validators=[DataRequired()])
    form_selection_build_version = SelectField('Choose a version of the model builder', validators=[DataRequired()])
    form_selection_number_of_epochs = SelectField('Choose the number of epochs to run the training', validators=[DataRequired()])
    form_selection_number_of_sentences = SelectField('Choose the subset of sentences', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PopulateTablesForm(FlaskForm):
    submit = SubmitField('Load Tables')
