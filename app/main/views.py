from datetime import datetime

from flask import render_template, session, redirect, url_for, current_app, flash
from .. import db
from ..models import Translation, Language, TranslationModel, BuildVersion, Epoch, Subset
from ..email import send_email
from ..translator import Translator
from . import main
from .forms import TranslationForm, BuildModelForm, PopulateTablesForm


@main.route('/', methods=['GET', 'POST'])
def index():
    
    form = TranslationForm()
    tr = Translator()
    
    # FORM POPULATION
    # Populate the dropdowns from the Language db
    # languages in Language are tagged as 'input' and/or 'output'
    form.form_selection_input_lang.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_source_lang=True).all()]
    form.form_selection_output_lang.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_target_lang=True).all()]

    if form.validate_on_submit():
        
        # Load the data from the form into memory
        input_text = form.form_string_input.data
        input_lang = form.form_selection_input_lang.data
        output_lang = form.form_selection_output_lang.data
        
        input_text_already_translated = Translation.query.filter_by(source_txt=input_text).first()  
        if input_text_already_translated is None:
            input = Translation(source_txt=input_text)
            db.session.add(input)
            db.session.commit()
            session['known'] = False
        else:
            # Run the translation on input_text
            output_text = tr.translate(input=input_text, lang=output_lang)
            session['known'] = True
        
        session['form_input'] = input_text
        session['input_lang'] = input_lang
        session['output_lang'] = output_lang

        # REPLACE the call to tr.translate() EVENTUALLY with table query of output
        session['form_output'] = tr.translate(input=input_text, lang=output_lang) #output_text
        
        return redirect(url_for('.index'))
    
    # FORM PERSISTENCE
    # Make the selected form values persistent after each translation by resetting the form
    # to the values in the session[] dictionary
    # But the session keys won't exist if it's the first session of the browser
    if 'form_input' in session:
        form.form_string_input.data= session['form_input']
    if 'input_lang' in session:
        form.form_selection_input_lang.data = session['input_lang']
    if 'output_lang' in session:
        form.form_selection_output_lang.data= session['output_lang']
        
        
        
    return render_template('index.html',
                           form=form,
                           form_output=session.get('form_output'),
                           form_input=session.get('form_input'), 
                           ouput_selection=session.get('output_lang'),
                           input_selection=session.get('input_lang'),             
                           known=session.get('known', False),
                           current_time=datetime.utcnow())



@main.route('/themodels', methods=['GET', 'POST'])
def themodels():
    
    # FORM POPULATION
    # Populate the dropdowns from the look-up tables 
    form = BuildModelForm()
    
    form.form_selection_input_lang.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_source_lang=True).all()]
    form.form_selection_output_lang.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_target_lang=True).all()]
    form.form_selection_build_version.choices = [f'{build.version_num}' for build in BuildVersion.query.all()]
    form.form_selection_number_of_epochs.choices = [f'{epoch.number_of_epochs}' for epoch in Epoch.query.all()]
    form.form_selection_number_of_sentences.choices = [f'{subset.number_of_sentences}' for subset in Subset.query.all()]

    if form.validate_on_submit():

        # Load the data from the form into memory
        input_lang = form.form_selection_input_lang.data
        output_lang = form.form_selection_output_lang.data
        build_version = form.form_selection_build_version.data
        epochs = form.form_selection_number_of_epochs.data
        subset = form.form_selection_number_of_sentences.data

        
        session['input_lang'] = input_lang
        session['output_lang'] = output_lang
        session['build_version'] = build_version
        session['epochs'] = epochs
        session['subset'] = subset
        
        return redirect(url_for('.index'))

    return render_template('themodels.html',
                            form=form,
                            form_selection_input_lang=session.get('input_lang'),
                            form_selection_output_lang=session.get('output_lang'),
                            form_selection_build_version=session.get('build_version'),
                            form_selection_number_of_epochs=session.get('epochs'),
                            form_selection_number_of_sentences=session.get('subset'),
                            current_time=datetime.utcnow())




@main.route('/about', methods=['GET', 'POST'])
def about():

    form = PopulateTablesForm()
    ret_val = 'DB Updated'

    if form.validate_on_submit():
        
        french = Language(  code='fr',name='français', en_name='French', is_source_lang=False, is_target_lang=True)
        english = Language(  code='en',name='english', en_name='English', is_source_lang=True, is_target_lang=False)
        spanish = Language(  code='es',name='español', en_name='Spanish', is_source_lang=False, is_target_lang=True)
        italian = Language(  code='it',name='italiano', en_name='Italian', is_source_lang=False, is_target_lang=True)
        german = Language(  code='de',name='deutsch', en_name='German', is_source_lang=False, is_target_lang=True)
        turkish = Language( code='tk', name='türkçe', en_name='Turkish', is_source_lang=False, is_target_lang=True)
        language_list = [french, english, spanish, italian, turkish, german]

        # en_2_fr = TranslationModel (name='en_2_fr', source_lang_id=2, target_lang_id=1)
        # en_2_es = TranslationModel (name='en_2_es', source_lang_id=2, target_lang_id=3)
        # en_2_tk = TranslationModel (name='en_2_tk', source_lang_id=2, target_lang_id=4)
        # en_2_it = TranslationModel (name='en_2_it', source_lang_id=2, target_lang_id=5)
        # en_2_de = TranslationModel (name='en_2_de', source_lang_id=2, target_lang_id=6)
        # model_list = [en_2_fr, en_2_es, en_2_tk, en_2_it, en_2_de]
        try:
            db.session.add_all(language_list)
            db.session.commit() 
            flash('DB Tables Loaded') 

        except Exception as e:
            flash('Load Failed: ' + str(e))

        

    return render_template('about.html', form=form)    