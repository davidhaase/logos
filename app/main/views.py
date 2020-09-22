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
    
    # Populate the dropdowns from the Language db
    # languages in Language are tagged as 'input' and/or 'output'
    form.form_input_lang_selection.choices = [f'{lang.en_name} ({lang.name})' for lang in Language.query.filter_by(is_source_lang=True).all()]
    form.form_output_lang_selection.choices = [f'{lang.en_name} ({lang.name})'  for lang in Language.query.filter_by(is_target_lang=True).all()]

    tr = Translator()
    if form.validate_on_submit():
        input = Translation.query.filter_by(source_txt=form.form_input.data).first()
        if input is None:
            input = Translation(source_txt=form.form_input.data)
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
