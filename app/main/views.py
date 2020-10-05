import os
from datetime import datetime
import json
import pickle
import re

from ..utils import S3File, seconds_to_string

from flask import render_template, session, redirect, url_for, current_app, flash
from .. import db
from ..models import Translation, Language, TranslationModel, Build, Epoch, Subset
from ..dynamo import dynoTranslation, DynoLanguage, DynoModel
from ..translator import Translator
from . import main
from .forms import TranslationForm, BuildModelForm, PopulateTablesForm
from .. import config
from .. import logging as log
# log = logging.getLogger(__name__)


# from ..filemanager import create_file

@main.route('/', methods=['GET', 'POST'])
def index():
    # LOAD VARIABLES for the PAGE in GENERAL
    # Display a table of all the translations made so far
    Translations = dynoTranslation()
    table_of_translation_history = [
        [   datetime.strptime(translation['date_created'], "%m/%d/%Y, %H:%M:%S"),
            translation['input_string'],
            translation['source_lang_en'],
            translation['output_string'],
            translation['target_lang_en'],
            translation['model_name'],
            translation['duration']
        ]
        for translation in Translations.scan()
    ]

    
    # LOAD VARIABLES for the FORM
    # Query the TranstionModel table to determine which languages are available as source and target
    # Populate the user options based on these availabilities
    form = TranslationForm()
    Models = DynoModel()
    form.form_selection_model.choices = Models.get_distinct('model_name')
    form.form_selection_input_lang.choices = Models.get_distinct('source_lang_en')
    form.form_selection_output_lang.choices =Models.get_distinct('target_lang_en')
    
    # USER CLICKS SUBMIT (FORM EVENT) - Build a new record and add it to the Translation table
    if form.validate_on_submit():

        # Load the data from the form into memory
        model_name = form.form_selection_model.data
        input_text = form.form_string_input.data
        input_lang = form.form_selection_input_lang.data
        output_lang = form.form_selection_output_lang.data
        output_text = ''
        
        
        # Model IDs are unique by: name, source language and target language
        # NOTE:  Model names are not unique
        # kwargs = {'engine':'devX', 'model_name': model_name, 'source_lang_en':input_lang, 'target_lang_en':output_lang}
        print(f'a new model_name is {model_name}')
        model = TranslationModel.query.filter_by(   name=model_name,
                                                    source_lang_id=Language.query.filter_by(en_name = input_lang).first().id,
                                                    target_lang_id=Language.query.filter_by(en_name = output_lang).first().id).first()


        # CHECK FOR CACHED TRANSLATIONS FIRST
        existing_translation = Translation.query.filter_by(model_id=model.id, source_txt=input_text).first()
        if existing_translation is None:
            
            # CHECK FOR LOCAL FILES: model.h5, source_tokenizer.pkl, & target_tokenizer.pkl
            # Keep in mind that the paths defined in the DB are relative: they start at /data/...
            # ...so get the full path to the app directory set in the the CONFIG
            app_dir = current_app.config['APP_DIR']
            full_path_to_model = f'{app_dir}/{model.model_path}'
            full_path_to_source_tokenizer = f'{app_dir}/{model.source_tokenizer}'
            full_path_to_target_tokenizer = f'{app_dir}/{model.target_tokenizer}'

            # First confirm that the three files exist locally: model.ht, source_tokenize.pkl, target_tokenizer.pkl
            # If they don't exist, you'll have to fetch them from AWS S3
            if not os.path.exists(full_path_to_model):
                
                # Do a quick check to see if all the partent directories are there first
                model_dir = os.path.abspath(os.path.dirname(full_path_to_model))
                if not os.path.exists(model_dir):
                    os.makedirs(model_dir)
                
                # Now fetch the files from AWS S3
                file_in_cloud = S3File(model.aws_bucket_name, model.model_path)
                file_in_cloud.copy_from_S3_to(full_path_to_model)

            if not os.path.exists(full_path_to_source_tokenizer):
                file_in_cloud = S3File(model.aws_bucket_name, model.source_tokenizer)
                file_in_cloud.copy_from_S3_to(full_path_to_source_tokenizer)

            if not os.path.exists(full_path_to_target_tokenizer):    
                file_in_cloud = S3File(model.aws_bucket_name, model.target_tokenizer)
                file_in_cloud.copy_from_S3_to(full_path_to_target_tokenizer)

            
            # This dict() is passed to the Translator model
            model_prefs = { 'model_path': f'{app_dir}/{model.model_path}',
                            'source_tokenizer' : pickle.load(open(f'{app_dir}/{model.source_tokenizer}', 'rb')),
                            'source_word_count' : model.source_word_count,
                            'source_max_length' : model.source_max_length,
                            'target_tokenizer' : pickle.load(open(f'{app_dir}/{model.target_tokenizer}', 'rb')),
                            'target_word_count' : model.target_word_count,
                            'target_max_length' : model.target_max_length }

            # HERE IS THE TRANSLATION PIECE
            # Start a timer to see how long it takes to translate
            start_time = datetime.utcnow()
            tr = Translator(model_prefs)
            output_text = tr.translate(input_text)

            # Tag it with the date and duration for curiosity
            date=datetime.utcnow()
            elapsed_time = date-start_time
            session['known'] = False
            
            # ADD TO THE DB
            try:
                input = Translation(model_id=model.id,
                                    source_txt=input_text, 
                                    target_txt=output_text, 
                                    elapsed_time=seconds_to_string(elapsed_time.seconds),
                                    date=date)
                db.session.add(input)
                db.session.commit()

                translation = dynoTranslation()
                translation_record={
                    'model_name' : model_name,
                    'input_string' : input_text,
                    'source_lang_en' : input_lang,
                    'output_string' : output_text,
                    'target_lang_en' : output_lang,
                    'duration' : seconds_to_string(elapsed_time.seconds),
                    'date_created' : date.strftime("%m/%d/%Y, %H:%M:%S")
                }
                response = translation.put_item(translation_record)

            except Exception as e:
                flash(f'Error: not able to add translation to database; {e}') 
        
        # The translation alrady exist for this model and languages so used the cached version
        else:
            session['known'] = True
            output_text = existing_translation.target_txt
               
        # SAVE BROWSER SESSION
        # (NB: this is NOT the db session)
        session['model_name'] = model_name
        session['input_text'] = input_text
        session['input_lang'] = input_lang
        session['output_lang'] = output_lang
        session['table_of_translation_history'] = table_of_translation_history
        session['form_output'] = output_text
        
        return redirect(url_for('.index'))
    
    # MAKE FORM PERSISTENT with BROWSER SESSION VARIABLES
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
                           known=session.get('known', False),
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

    if form.validate_on_submit():
        
        # BUILD LANGUAGE TABLE in AWS
        # One-time code to build language table from json file in json dir
        # Languages = DynoLanguage()
        # json_file = current_app.config['APP_DIR'] + '/bin/json/languagedata.json'
         
        # with open(json_file) as json_file:
        #     language_list = json.load(json_file)
        # form_list = [Languages.load_items(language_list)]

        # BUILD MODEL TABLE in AWS
        # This is one-time code to rebuild the model table from what it finds on S3
        # Crawls S3 to see what models are there and derives the tables values from the structure
        # Models = DynoModel()
        # s3_dir = S3File('logos-models', 'data')
        # form_list = []

        # relative_path = 'data/models/'
        # list_of_models = s3_dir.crawl_models('data/models')
        # for engine in list_of_models:
        #     for model in list_of_models[engine]:
        #         for source in list_of_models[engine][model]:
        #             for target in list_of_models[engine][model][source]:
        #                 path = f'{relative_path}{engine}/{model}/{source}/{target}/'
        #                 form_list.append(path)
        #                 source_tokenizer_file = path + 'source_tokenizer.pkl'
        #                 target_tokenizer_file = path + 'target_tokenizer.pkl'
        #                 model_path= path + 'model.h5'
                        
        #                 ### THESE ARE HACKS FOR THE MOMENT
        #                 if ('75K' in model):
        #                   sentences = 75
        #                 else:
        #                     sentences = 50
        #                 epochs = 35

        #                 app_dir = current_app.config['APP_DIR']
        #                 target_pkl = f'{app_dir}/tmp/model_prefs.pkl'
        #                 s3_pkl = f'{path}pickles/model_prefs.pkl'
                        
        #                 pickled_file = S3File('logos-models', s3_pkl)
        #                 pickled_file.copy_from_S3_to(target_pkl)
        #                 model_prefs = pickle.load(open(target_pkl, 'rb'))
                        

        #                 ### End hacks

        #                 date = datetime.utcnow()
        #                 model_record = { 'engine' : engine,
        #                     'model_id' : f'{model}_{source}_{target}',
        #                     'model_name' : model,
        #                     'date_created' : date.strftime("%m/%d/%Y, %H:%M:%S"),
        #                     'source_lang_en' : source,
        #                     'target_lang_en' : target,
        #                     'engine' : engine,
        #                     'epochs' : epochs,
        #                     'subset' : sentences,
        #                     'source_tokenizer_path' : source_tokenizer_file,
        #                     'source_max_length' : model_prefs['source_max_length'],
        #                     'target_tokenizer_path' : target_tokenizer_file,
        #                     'target_max_length' : model_prefs['target_max_length'],
        #                     'model_path' : model_path,
        #                     'aws_bucket_name' : 'logos-models'
        #                 }

        #                 try:
        #                     response = Models.put_item(model_record)
        #                 except Exception as e:
        #                     flash(f'unable to load db: {e}') 
        session['form_list'] = form_list
        return redirect(url_for('.about'))

    return render_template('about.html', form=form, form_list=session.get('form_list'))  
    

@main.route('/identify', methods=['GET', 'POST'])
def identify(): 
    return render_template('identify.html')  

@main.route('/diagnose', methods=['GET', 'POST'])
def diagnose(): 
    return render_template('diagnose.html')  