from datetime import datetime

from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import Translation, Language, TranslationModel
from ..email import send_email
from ..translator import Translator
from . import main
from .forms import TranslationForm


@main.route('/', methods=['GET', 'POST'])
def index():
    
    form = TranslationForm()
    tr = Translator()
    
    # FORM POPULATION
    # Populate the dropdowns from the Language db
    # languages in Language are tagged as 'input' and/or 'output'
    form.form_input_lang_selection.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_source_lang=True).all()]
    form.form_output_lang_selection.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_target_lang=True).all()]

    if form.validate_on_submit():
        
        # Load the data from the form into memory
        input_text = form.form_input.data
        input_lang = form.form_input_lang_selection.data
        output_lang = form.form_output_lang_selection.data
        output_text = tr.translate(input=input_text, lang=output_lang)
        
        input_text_already_translated = Translation.query.filter_by(source_txt=form.form_input.data).first()  
        if input_text_already_translated is None:
            input = Translation(source_txt=input_text)
            db.session.add(input)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['form_input'] = form.form_input.data
        session['input_lang'] = form.form_input_lang_selection.data
        session['output_lang'] = form.form_output_lang_selection.data
        session['form_output'] = tr.translate(input=form.form_input.data, lang=form.form_output_lang_selection.data)
        return redirect(url_for('.index'))
    
    # FORM PERSISTENCE
    # Make the selected form values persistent after each translation by resetting the form
    # to the values in the session[] dictionary
    # But the session keys won't exist if it's the first session of the browser
    if 'form_input' in session:
        form.form_input.data = session['form_input']
    if 'input_lang' in session:
        form.form_input_lang_selection.data = session['input_lang']
    if 'output_lang' in session:
        form.form_output_lang_selection.data = session['output_lang']
        
        
        
    return render_template('index.html',
                           form=form,
                           form_output=session.get('form_output'),
                           form_input=session.get('form_input'), 
                           ouput_selection=session.get('output_lang'),
                           input_selection=session.get('input_lang'),             
                           known=session.get('known', False),
                           current_time=datetime.utcnow())

@main.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@main.route('/themodels', methods=['GET', 'POST'])
def themodels():
    return render_template('themodels.html')
