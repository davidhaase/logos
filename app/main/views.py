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
    
    # LOAD FORM VARIABLES
    # Populate the user option for input and output languages from the Language look-up table

    form.form_selection_input_lang.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_source_lang=True).all()]
    form.form_selection_output_lang.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_target_lang=True).all()]

    # USER CLICKS SUBMIT (FORM EVENT) - Build a new record and add it to the Translation table
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
        
        # SAVE BROWSER SESSION
        # (NB: this is NOT the db session)
        session['form_input'] = input_text
        session['input_lang'] = input_lang
        session['output_lang'] = output_lang

        # REPLACE this call to tr.translate() EVENTUALLY with table query of output
        session['form_output'] = tr.translate(input=input_text, lang=output_lang) #output_text
        
        return redirect(url_for('.index'))
    
    # LOAD SESSION VARIABLES (for Persistence)
    # Make the selected form values persistent after each translation by resetting the form
    # ...to the values in the session[] dictionary
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
    
    # LOAD PAGE VARIABLES
    # Display a table of all the models built so far
    table_of_model_history = [[model.id, model.date, model.name] for model in TranslationModel.query.all()]

    # LOAD FORM VARIABLES
    # Populate all the user dropdown options from the db look-up tables 
    form = BuildModelForm()
    
    form.form_selection_input_lang.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_source_lang=True).all()]
    form.form_selection_output_lang.choices = [f'{lang.en_name}' for lang in Language.query.filter_by(is_target_lang=True).all()]
    form.form_selection_build_version.choices = [f'{build.version_num}' for build in BuildVersion.query.all()]
    form.form_selection_number_of_epochs.choices = [f'{epoch.number_of_epochs}' for epoch in Epoch.query.all()]
    form.form_selection_number_of_sentences.choices = [f'{subset.display_string_of_number}' for subset in Subset.query.all()]

    # USER CLICKS SUBMIT (FORM EVENT) - Build a new model record and add it to the TranslationModel table
    if form.validate_on_submit():

        # If the model doesn't exist already, use the vars below 
        # ...to define a new model in the TranslationModel table
        # ...by loading the submitted form data into memory
        input_lang = form.form_selection_input_lang.data
        output_lang = form.form_selection_output_lang.data
        build_version = form.form_selection_build_version.data
        epochs = form.form_selection_number_of_epochs.data
        subset = form.form_selection_number_of_sentences.data
        date = datetime.utcnow()

        # Create a unique and descriptive name for the model
        name = f'{input_lang}_to_{output_lang}_from_{build_version}_with_{epochs}e_on_{subset}sents'

        # Check to see if the model already exists.
        model_name = TranslationModel.query.filter_by(name=name).first()  
        if model_name is None:
            try:
                model_name = TranslationModel(name=name,
                                              date=date,
                                              source_lang_id=Language.query.filter_by(en_name=input_lang).first().id,
                                              target_lang_id=Language.query.filter_by(en_name=output_lang).first().id,
                                              build_id=BuildVersion.query.filter_by(version_num=build_version).first().id)
                db.session.add(model_name)
                db.session.commit()
                flash(f'Model added: {model_name}') 
                session['known'] = False
            except Exception as e:
                flash(f'Error: not able to add {model_name}') 

        else:
            flash(f'Warning: Not rebuilding as model already exists; using: {model_name}') 
            # Run the translation on input_text
            # output_text = tr.translate(input=input_text, lang=output_lang)
            session['known'] = True

        # SAVE BROWSER SESSION
        # (NB: this is NOT the db session)
        session['input_lang'] = input_lang
        session['output_lang'] = output_lang
        session['build_version'] = build_version
        session['epochs'] = epochs
        session['subset'] = subset
        
        return redirect(url_for('.themodels'))
    
    # LOAD SESSION VARIABLES (for Persistence)
    # Make the selected form values persistent after each translation by resetting the form
    # ...to the values in the session[] dictionary
    # But the session keys won't exist if it's the first session of the browser
    if 'input_lang' in session:
        form.form_selection_input_lang.data = session['input_lang']
    if 'output_lang' in session:
        form.form_selection_output_lang.data= session['output_lang']
    if 'build_version' in session:
        form.form_selection_build_version.data= session['build_version']
    if 'epochs' in session:
        form.form_selection_number_of_epochs.data= session['epochs']
    if 'subset' in session:
        form.form_selection_number_of_sentences.data= session['subset']

    return render_template('themodels.html',
                            form=form,
                            form_selection_input_lang=session.get('input_lang'),
                            form_selection_output_lang=session.get('output_lang'),
                            form_selection_build_version=session.get('build_version'),
                            form_selection_number_of_epochs=session.get('epochs'),
                            form_selection_number_of_sentences=session.get('subset'),
                            table_of_model_history=table_of_model_history,
                            current_time=datetime.utcnow())




@main.route('/about', methods=['GET', 'POST'])
def about():

    form = PopulateTablesForm()
    ret_val = 'DB Updated'

    if form.validate_on_submit():
        
        french = Language(  code='fr',name='français', en_name='French', is_source_lang=True, is_target_lang=True)
        english = Language(  code='en',name='english', en_name='English', is_source_lang=True, is_target_lang=True)
        spanish = Language(  code='es',name='español', en_name='Spanish', is_source_lang=True, is_target_lang=True)
        italian = Language(  code='it',name='italiano', en_name='Italian', is_source_lang=True, is_target_lang=True)
        german = Language(  code='de',name='deutsch', en_name='German', is_source_lang=True, is_target_lang=True)
        turkish = Language( code='tk', name='türkçe', en_name='Turkish', is_source_lang=True, is_target_lang=True)
        language_list = [french, english, spanish, italian, turkish, german]

        ten = Epoch(number_of_epochs=10)
        twenty = Epoch(number_of_epochs=20)
        thirty_five = Epoch(number_of_epochs=35)
        fifty = Epoch(number_of_epochs=50)
        seventy_five = Epoch(number_of_epochs=75)
        one_hundred = Epoch(number_of_epochs=100)
        one_fifty = Epoch(number_of_epochs=150)
        epoch_list = [ten, twenty, thirty_five, fifty, seventy_five, one_hundred, one_fifty]

        ten_k = Subset(number_of_sentences=10000, display_string_of_number='10K')
        twenty_k = Subset(number_of_sentences=20000, display_string_of_number='20K')
        fifty_k = Subset(number_of_sentences=50000, display_string_of_number='50K')
        seventy_five_k = Subset(number_of_sentences=75000, display_string_of_number='75K')
        hundred_k = Subset(number_of_sentences=100000, display_string_of_number='100K')
        subset_list = [ten_k, twenty_k, fifty_k, seventy_five_k, hundred_k]

        empty_build = BuildVersion(version_num='dev_00', summary='No translation model is implemented; just string changes')

        try:
            db.session.add_all(language_list)
            db.session.add_all(epoch_list)
            db.session.add_all(subset_list)
            db.session.add(empty_build)
            db.session.commit() 
            flash('DB Tables Loaded') 

        except Exception as e:
            flash('Load Failed: ' + str(e))

        return redirect(url_for('.about'))

        

    return render_template('about.html', form=form)    