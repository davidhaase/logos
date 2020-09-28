import os
from datetime import datetime
import pickle

from flask import render_template, session, redirect, url_for, current_app, flash
from .. import db
from ..models import Translation, Language, TranslationModel, Build, Epoch, Subset
from ..translator import Translator
from . import main
from .forms import TranslationForm, BuildModelForm, PopulateTablesForm


@main.route('/', methods=['GET', 'POST'])
def index():
    
    form = TranslationForm()
    tr = Translator()

    # LOAD PAGE VARIABLES
    # Display a table of all the translations made so far
    table_of_translation_history = [[   translation.id, 
                                        translation.date, 
                                        translation.source_txt, 
                                        translation.target_txt,
                                        TranslationModel.query.filter_by(id=translation.model_id).first().name] \
        for translation in Translation.query.all()]

    
    # LOAD FORM VARIABLES
    # Query the TranstionModel table to determine which languages are available as source and target
    # Populate the user options based on these availabilities
    
    # model selection
    form.form_selection_model.choices = [f'{model.name}' for model in db.session.query(TranslationModel.name).distinct()]
    
    # input/source language selection
    form.form_selection_input_lang.choices = [f'{Language.query.filter_by(id=model.source_lang_id).first().en_name}' \
        for model in db.session.query(TranslationModel.source_lang_id).distinct()]
    
    # output/target language selection
    form.form_selection_output_lang.choices = [f'{Language.query.filter_by(id=model.target_lang_id).first().en_name}' \
        for model in db.session.query(TranslationModel.target_lang_id).distinct()]

    # USER CLICKS SUBMIT (FORM EVENT) - Build a new record and add it to the Translation table
    if form.validate_on_submit():
        
        # Load the data from the form into memory
        model_name = form.form_selection_model.data
        input_text = form.form_string_input.data
        input_lang = form.form_selection_input_lang.data
        output_lang = form.form_selection_output_lang.data
        output_text = ''
        
        # input_text_already_translated = Translation.query.filter_by(source_txt=input_text).first()  
        # if input_text_already_translated is None:
        output_text = tr.translate(input=input_text, lang=output_lang, path_to_model='AWS')
        input = Translation(    model_id=TranslationModel.query.filter_by(name=model_name).first().id,
                                source_txt=input_text, 
                                target_txt=output_text, 
                                date=datetime.utcnow())
        db.session.add(input)
        db.session.commit()
        # session['known'] = False
        # else:
            # Run the translation on input_text
            # path_to_model = '/Users/davidhaase/Documents/Learn/Flatiron/Projects/machine-translator/models/de_to_en/basic_75K_35E_fixed/pickles'
            # path_to_pickle = path_to_model + '/model_prefs.pkl'
            # model_prefs = pickle.load(open(path_to_pickle, 'rb'))
            # TRANSLATOR_MODEL_LOCATION = os.environ.get('TRANSLATOR_MODEL_LOCATION')
            
            # session['known'] = True
        
        # SAVE BROWSER SESSION
        # (NB: this is NOT the db session)
        session['model_name'] = model_name
        session['input_text'] = input_text
        session['input_lang'] = input_lang
        session['output_lang'] = output_lang

        # REPLACE this call to tr.translate() EVENTUALLY with table query of output
        session['form_output'] = output_text #tr.translate(input=input_text, lang=output_lang, path_to_model='AWS')
        
        return redirect(url_for('.index'))
    
    # LOAD SESSION VARIABLES (for Persistence)
    # Make the selected form values persistent after each translation by resetting the form
    # ...to the values in the session[] dictionary
    # But the session keys won't exist if it's the first session of the browser
    if 'model_name' in session:
        form.form_selection_model.data = session['model_name']
    if 'input_text' in session:
        form.form_string_input.data= session['input_text']
    if 'input_lang' in session:
        form.form_selection_input_lang.data = session['input_lang']
    if 'output_lang' in session:
        form.form_selection_output_lang.data= session['output_lang']
        
        
        
    return render_template('index.html',
                           form=form,
                           form_output=session.get('form_output'),
                           form_input=session.get('input_text'), 
                           ouput_selection=session.get('output_lang'),
                           input_selection=session.get('input_lang'),             
                        #    known=session.get('known', False),
                           table_of_translation_history=table_of_translation_history,
                           current_time=datetime.utcnow())



@main.route('/themodels', methods=['GET', 'POST'])
def themodels():
    
    # LOAD PAGE VARIABLES
    # Display a table of all the models built so far
    table_of_model_history = [[model.id, 
                               model.date, 
                               model.name, 
                               Language.query.filter_by(id=model.source_lang_id).first().en_name, 
                               Language.query.filter_by(id=model.target_lang_id).first().en_name,
                               Build.query.filter_by(id=model.build_id).first().name,
                               model.number_of_epochs,
                               model.number_of_sentences] \
                                   for model in TranslationModel.query.all()]

    # LOAD FORM VARIABLES
    # Populate all the user dropdown options from the db look-up tables 
    form = BuildModelForm()
    
    form.form_selection_input_lang.choices = [f'{lang.en_name}' for lang in Language.query.all()]
    form.form_selection_output_lang.choices = [f'{lang.en_name}' for lang in Language.query.all()]
    form.form_selection_build_name.choices = [f'{build.name}' for build in Build.query.all()]
    form.form_selection_number_of_epochs.choices = [f'{epoch.number_of_epochs}' for epoch in Epoch.query.all()]
    form.form_selection_number_of_sentences.choices = [f'{subset.display_string_of_number}' for subset in Subset.query.all()]

    # USER CLICKS SUBMIT (FORM EVENT) - Build a new model record and add it to the TranslationModel table
    if form.validate_on_submit():

        # If the model doesn't exist already, use the vars below 
        # ...to define a new model in the TranslationModel table
        # ...by loading the submitted form data into memory
        input_lang = form.form_selection_input_lang.data
        output_lang = form.form_selection_output_lang.data
        build_name = form.form_selection_build_name.data
        epochs = form.form_selection_number_of_epochs.data
        subset = form.form_selection_number_of_sentences.data
        date = datetime.utcnow()

        
        # Create a unique and descriptive name for the model
        name = f'{build_name}_{epochs}e_{subset}s'

        # Query by name, source_lang and target_lang to see if the model exists
        # Don't rebuild if it already exists for the desired languages
        model = TranslationModel.query.filter_by(name=name,
                                                    source_lang_id=Language.query.filter_by(en_name=input_lang).first().id,
                                                    target_lang_id=Language.query.filter_by(en_name=output_lang).first().id,).first()  
        
        # The model doesn't yet exist for these languages, so build it
        if model is None:
            try:
                model = TranslationModel(name=name,
                                            date=date,
                                            source_lang_id=Language.query.filter_by(en_name=input_lang).first().id,
                                            target_lang_id=Language.query.filter_by(en_name=output_lang).first().id,
                                            build_id=Build.query.filter_by(name=build_name).first().id,
                                            number_of_epochs=epochs,
                                            number_of_sentences=subset)
                db.session.add(model)
                db.session.commit()
                flash(f'Model added: {model.name}') 
                session['known'] = False
            except Exception as e:
                flash(f'Error: not able to add {model.name} {e}') 

        else:
            flash(f'Warning: Not rebuilding as model already exists; using: {model.name}') 
            # Run the translation on input_text
            # output_text = tr.translate(input=input_text, lang=output_lang)
            session['known'] = True

        # SAVE BROWSER SESSION
        # (NB: this is NOT the db session)
        session['input_lang'] = input_lang
        session['output_lang'] = output_lang
        session['build_name'] = build_name
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
    if 'build_name' in session:
        form.form_selection_build_name.data= session['build_name']
    if 'epochs' in session:
        form.form_selection_number_of_epochs.data= session['epochs']
    if 'subset' in session:
        form.form_selection_number_of_sentences.data= session['subset']

    return render_template('themodels.html',
                            form=form,
                            form_selection_input_lang=session.get('input_lang'),
                            form_selection_output_lang=session.get('output_lang'),
                            form_selection_build_name=session.get('build_name'),
                            form_selection_number_of_epochs=session.get('epochs'),
                            form_selection_number_of_sentences=session.get('subset'),
                            table_of_model_history=table_of_model_history,
                            current_time=datetime.utcnow())




@main.route('/about', methods=['GET', 'POST'])
def about():

    form = PopulateTablesForm()
    ret_val = 'DB Updated'

    if form.validate_on_submit():
        
        french = Language(  code='fr',name='français', en_name='French')
        english = Language(  code='en',name='english', en_name='English')
        spanish = Language(  code='es',name='español', en_name='Spanish')
        italian = Language(  code='it',name='italiano', en_name='Italian')
        german = Language(  code='de',name='deutsch', en_name='German')
        turkish = Language( code='tr', name='türkçe', en_name='Turkish')
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

        empty_build = Build(name='dev_00', summary='No translation model is implemented; just string changes')

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


@main.route('/identify', methods=['GET', 'POST'])
def identify(): 
    return render_template('identify.html')  

@main.route('/diagnose', methods=['GET', 'POST'])
def diagnose(): 
    return render_template('diagnose.html')  