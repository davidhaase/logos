import os
from datetime import datetime
from decimal import Decimal
import json
import pickle
import re

from flask import render_template, session, redirect, url_for, current_app, flash

from .. import db
from .. import config
from .. import logging
logger = logging.getLogger(__name__)

from . import main
from .forms import TranslationForm, BuildModelForm, PopulateTablesForm

from ..dynamo import Translation, Language, Model
from ..translator import Translator
from ..utils import S3File, seconds_to_string






# from ..filemanager import create_file

@main.route('/', methods=['GET', 'POST'])
def index():
    # LOAD VARIABLES for the PAGE in GENERAL
    # Display a table of all the translations made so far
    Translations = Translation()
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
    Models = Model()
    form.form_selection_build.choices = Models.get_distinct('build_name')
    form.form_selection_input_lang.choices = Models.get_distinct('source_lang_en')
    form.form_selection_output_lang.choices =Models.get_distinct('target_lang_en')

    logger.info(f'logger.info from {__file__} and {__name__}')
    
    # USER CLICKS SUBMIT (FORM EVENT) - Build a new record and add it to the Translation table
    if form.validate_on_submit():

        # Start a timer to see how long it takes to translate
        start_time = datetime.utcnow()
        logger.info('logger.info with level=INFO AFTER CLICK')

        # Load the data from the form into memory
        build_name = form.form_selection_build.data
        input_string = form.form_string_input.data
        source_lang_en = form.form_selection_input_lang.data
        target_lang_en = form.form_selection_output_lang.data
        output_string = ''
        
        # Model names are unique by concatenating the model attributes
        model = Models.get_model(f'{build_name}_{source_lang_en}_{target_lang_en}')
        
        # CHECK FOR CACHED TRANSLATIONS FIRST
        already_translated = Translations.get_translation(model['model_name'], input_string)
        if not already_translated:
            
            # CHECK FOR LOCAL FILES: model.h5, source_tokenizer.pkl, & target_tokenizer.pkl
            # Keep in mind that the paths defined in the DB are relative: they start at /data/...
            # ...so get the full path to the app directory set in the the CONFIG
            app_dir = current_app.config['APP_DIR']
            full_path_to_model = f'{app_dir}/{model["model_path"]}'
            full_path_to_source_tokenizer = f'{app_dir}/{model["source_tokenizer_path"]}'
            full_path_to_target_tokenizer = f'{app_dir}/{model["target_tokenizer_path"]}'

            # First confirm that the three files exist locally: model.ht, source_tokenize.pkl, target_tokenizer.pkl
            # If they don't exist, you'll have to fetch them from AWS S3
            if not os.path.exists(full_path_to_model):
                
                # Do a quick check to see if all the partent directories are there first
                model_dir = os.path.abspath(os.path.dirname(full_path_to_model))
                if not os.path.exists(model_dir):
                    os.makedirs(model_dir)
                
                # Now fetch the files from AWS S3
                file_in_cloud = S3File(model['aws_bucket_name'], model['model_path'])
                file_in_cloud.copy_from_S3_to(full_path_to_model)

            if not os.path.exists(full_path_to_source_tokenizer):
                file_in_cloud = S3File(model['aws_bucket_name'], model['source_tokenizer_path'])
                file_in_cloud.copy_from_S3_to(full_path_to_source_tokenizer)

            if not os.path.exists(full_path_to_target_tokenizer):    
                file_in_cloud = S3File(model['aws_bucket_name'], model['target_tokenizer_path'])
                file_in_cloud.copy_from_S3_to(full_path_to_target_tokenizer)

            
            # This dict() is passed to the Translator model
            model_prefs = { 'model_path': f'{app_dir}/{model["model_path"]}',
                            'source_tokenizer' : pickle.load(open(f'{app_dir}/{model["source_tokenizer_path"]}', 'rb')),
                            'source_word_count' : model['source_word_count'],
                            'source_max_length' : model['source_max_length'],
                            'target_tokenizer' : pickle.load(open(f'{app_dir}/{model["target_tokenizer_path"]}', 'rb')),
                            'target_word_count' : model['target_word_count'],
                            'target_max_length' : model['target_max_length'] }

            # HERE IS THE TRANSLATION PIECE
            tr = Translator(model_prefs)
            output_string = tr.translate(input_string)

            # Tag it with the date and duration for curiosity
            date=datetime.utcnow()
            elapsed_time = date-start_time
            session['known'] = False
            
            # ADD TO THE DB
            try:
                translation = Translation()
                translation_record={
                    'model_name' : model['model_name'],
                    'input_string' : input_string,
                    'source_lang_en' : source_lang_en,
                    'output_string' : output_string,
                    'target_lang_en' : target_lang_en,
                    'duration' : seconds_to_string(elapsed_time.seconds),
                    'date_created' : date.strftime("%m/%d/%Y, %H:%M:%S")
                }
                response = translation.put_item(translation_record)
                flash(f'Tranlsation added to DB')

            except Exception as e:
                flash(f'Error: not able to add translation to database; {e}') 
        
        # # The translation already exists for this model so used the cached version
        else:
            session['known'] = True
            output_string = already_translated['output_string']
               
        # SAVE BROWSER SESSION
        # (NB: this is NOT the db session)
        session['build_name'] = build_name
        session['input_string'] = input_string
        session['source_lang_en'] = source_lang_en
        session['target_lang_en'] = target_lang_en
        session['table_of_translation_history'] = table_of_translation_history
        session['output_string'] = output_string
        
        return redirect(url_for('.index'))
    
    # MAKE FORM PERSISTENT with BROWSER SESSION VARIABLES
    # Make the selected form values persistent after each translation by resetting the form
    # ...to the values in the session[] dictionary
    # But the session keys won't exist if it's the first session of the browser
    if 'build_name' in session:
        form.form_selection_build.data = session['build_name']
    if 'input_string' in session:
        form.form_string_input.data= session['input_string']
    if 'source_lang_en' in session:
        form.form_selection_input_lang.data = session['source_lang_en']
    if 'target_lang_en' in session:
        form.form_selection_output_lang.data= session['target_lang_en']
        

        
        
    return render_template(
        'index.html',
        form=form,
        output_string=session.get('output_string'),
        form_input=session.get('input_string'), 
        ouput_selection=session.get('target_lang_en'),
        input_selection=session.get('source_lang_en'),             
        known=session.get('known', False),
        table_of_translation_history=table_of_translation_history,
        current_time=datetime.utcnow()
    )



@main.route('/themodels', methods=['GET', 'POST'])
def themodels():
    
    # LOAD VARIABLES for the PAGE in GENERAL
    # Display a table of all the translations made so far
    Models = Model()
    table_of_model_history = [
        [   model['model_name'],
            model['engine'],
            model['subset'],
            model['epochs'],
            model['source_lang_en'],
            model['target_lang_en'],
            datetime.strptime(model['date_created'], "%m/%d/%Y, %H:%M:%S")
        ]
        for model in Models.scan()
    ]
    return render_template(
        'themodels.html',
        table_of_model_history=table_of_model_history,
        current_time=datetime.utcnow()
    )
    

    # LOAD FORM VARIABLES
    # Populate all the user dropdown options from the db look-up tables 
    # form = BuildModelForm()
    
    # form.form_selection_source_lang_en.choices = Languages.get_distinct('en_name')
    # form.form_selection_target_lang_en.choices = Languages.get_distinct('en_name')
    # form.form_selection_engine.choices = Models.get_distinct('engine')
    # form.form_selection_number_of_epochs.choices = Models.get_distinct('engine')
    # form.form_selection_number_of_sentences.choices = [f'{subset.display_string_of_number}' for subset in Subset.query.all()]

    # USER CLICKS SUBMIT (FORM EVENT) - Build a new model record and add it to the TranslationModel table
    # if form.validate_on_submit():

        # If the model doesn't exist already, use the vars below 
        # ...to define a new model in the TranslationModel table
        # ...by loading the submitted form data into memory
        # source_lang_en = form.form_selection_source_lang_en.data
        # target_lang_en = form.form_selection_target_lang_en.data
        # engine = form.form_selection_engine.data
        # epochs = form.form_selection_number_of_epochs.data
        # subset = form.form_selection_number_of_sentences.data
        # date = datetime.utcnow()

        
        # Create a unique and descriptive name for the model
        # model_name = f'{engine}__{subset}K_{epochs}E_{source_lang_en}_{target_lang_en}'

        # Query by name, source_lang and target_lang to see if the model exists
        # Don't rebuild if it already exists for the desired languages
        # model_record = { 
        # 'model_name' : f'{engine}_{source}_{target}',
        # 'engine' : engine,
        # 'date_created' : date.strftime("%m/%d/%Y, %H:%M:%S"),
        # 'source_lang_en' : source,
        # 'target_lang_en' : target,
        # 'engine' : engine,
        # 'epochs' : epochs,
        # 'subset' : subset,
        # 'source_tokenizer_path' : source_tokenizer_file,
        # 'source_max_length' : int(model_prefs['source_max_length']),
        # 'source_word_count' : int(model_prefs['source_vocab_size']),
        # 'target_tokenizer_path' : target_tokenizer_file,
        # 'target_max_length' : int(model_prefs['target_max_length']),
        # 'target_word_count' : int(model_prefs['target_vocab_size']),
        # 'model_path' : model_path,
        # 'aws_bucket_name' : 'logos-models',
        # 'training_counts' : {
        #     'total_count' : model_prefs['total_count'],
        #     'train_count' : model_prefs['train_count'],
        #     'test_count' : model_prefs['test_count']
        # },
        # 'BLEUs' : {
        #     'BLEU1': Decimal(model_prefs['BLEU1']),
        #     'BLEU2': Decimal(model_prefs['BLEU2']),
        #     'BLEU3': Decimal(model_prefs['BLEU3']),
        #     'BLEU4': Decimal(model_prefs['BLEU4'])
        # }                           
        # }

        # SAVE BROWSER SESSION
        # (NB: this is NOT the db session)
        # session['input_lang'] = input_lang
        # session['output_lang'] = output_lang
        # session['build_name'] = build_name
        # session['epochs'] = epochs
        # session['subset'] = subset
        
        # return redirect(url_for('.themodels'))
    
    # LOAD SESSION VARIABLES (for Persistence)
    # Make the selected form values persistent after each translation by resetting the form
    # ...to the values in the session[] dictionary
    # But the session keys won't exist if it's the first session of the browser
    # if 'source_lang_en' in session:
    #     form.form_selection_source_lang_en.data = session['source_lang_en']
    # if 'target_lang_en' in session:
    #     form.form_selection_target_lang_en.data= session['target_lang_en']
    # if 'engine' in session:
    #     form.form_selection_engine.data= session['engine']
    # if 'epochs' in session:
    #     form.form_selection_number_of_epochs.data= session['epochs']
    # if 'subset' in session:
    #     form.form_selection_number_of_sentences.data= session['subset']

    




@main.route('/about', methods=['GET', 'POST'])
def about():
    form = PopulateTablesForm()

    if form.validate_on_submit():
        
        # BUILD LANGUAGE TABLE in AWS
        # One-time code to build language table from json file in json dir
        Languages = Language()
        json_file = current_app.config['APP_DIR'] + '/bin/json/languagedata.json'
         
        with open(json_file) as json_file:
            language_list = json.load(json_file)
        form_list = [Languages.load_items(language_list)]

        # BUILD MODEL TABLE in AWS
        # This is one-time code to rebuild the model table from what it finds on S3
        # Crawls S3 to see what models are there and derives the tables values from the structure
        Models = Model()
        s3_dir = S3File('logos-models', 'data')
        form_list = []
        id = 0

        relative_path = 'data/models/'
        list_of_models = s3_dir.crawl_models('data/models')
        for engine in list_of_models:
            for build in list_of_models[engine]:
                for source in list_of_models[engine][build]:
                    for target in list_of_models[engine][build][source]:
                        path = f'{relative_path}{engine}/{build}/{source}/{target}/'
                        form_list.append(path)
                        source_tokenizer_file = path + 'source_tokenizer.pkl'
                        target_tokenizer_file = path + 'target_tokenizer.pkl'
                        model_path= path + 'model.h5'
                        
                        ### THESE ARE HACKS FOR THE MOMENT
                        if ('75K' in build):
                          sentences = 75
                        else:
                            sentences = 50
                        epochs = 35

                        app_dir = current_app.config['APP_DIR']
                        target_pkl = f'{app_dir}/tmp/model_prefs.pkl'
                        s3_pkl = f'{path}pickles/model_prefs.pkl'
                        
                        pickled_file = S3File('logos-models', s3_pkl)
                        pickled_file.copy_from_S3_to(target_pkl)
                        model_prefs = pickle.load(open(target_pkl, 'rb'))
                        # {'model_path': 'models/tr_to_en/basic_75K_35E_fixed/model.h5',
                        # 'source_tokenizer': <keras_preprocessing.text.Tokenizer object at 0x7fa9c3889160>,
                        # 'source_max_length': 9,
                        # 'source_vocab_size': 23521,
                        # 'target_tokenizer': <keras_preprocessing.text.Tokenizer object at 0x7fa9c3b90588>,
                        # 'target_vocab_size': 8183,
                        # 'target_max_length': 7,
                        # 'total_count': 500237,
                        # 'train_count': 67500,
                        # 'test_count': 7500,
                        # 'BLEU1': 0.6865620717271048,
                        # 'BLEU2': 0.5824291114596682, 
                        # 'BLEU3': 0.5292572641080151,
                        # 'BLEU4': 0.38655408626018345}
                        

                        ### End hacks
                        date = datetime.utcnow()
                        
                        model_record = { 
                            'model_name' : f'{build}_{source}_{target}',
                            'engine' : engine,
                            'build_name' : build,
                            'date_created' : date.strftime("%m/%d/%Y, %H:%M:%S"),
                            'source_lang_en' : source,
                            'target_lang_en' : target,
                            'engine' : engine,
                            'epochs' : epochs,
                            'subset' : sentences,
                            'source_tokenizer_path' : source_tokenizer_file,
                            'source_max_length' : int(model_prefs['source_max_length']),
                            'source_word_count' : int(model_prefs['source_vocab_size']),
                            'target_tokenizer_path' : target_tokenizer_file,
                            'target_max_length' : int(model_prefs['target_max_length']),
                            'target_word_count' : int(model_prefs['target_vocab_size']),
                            'model_path' : model_path,
                            'aws_bucket_name' : 'logos-models',
                            'training_counts' : {
                                'total_count' : model_prefs['total_count'],
                                'train_count' : model_prefs['train_count'],
                                'test_count' : model_prefs['test_count']
                            }#,
                            # 'BLEUs' : {
                            #     'BLEU1': Decimal(model_prefs['BLEU1']),
                            #     'BLEU2': Decimal(model_prefs['BLEU2']),
                            #     'BLEU3': Decimal(model_prefs['BLEU3']),
                            #     'BLEU4': Decimal(model_prefs['BLEU4'])
                            # }                           
                        }

                        try:
                            response = Models.put_item(model_record)
                        except Exception as e:
                            flash(f'unable to load db: {e}') 
        session['form_list'] = form_list
        return redirect(url_for('.about'))

    return render_template('about.html', form=form, form_list=session.get('form_list'))  
    
@main.route('/themodels/<model_name>', methods=['GET', 'POST'])
def modeldetail(model_name): 
    return render_template(
        'modeldetail.html',
        model_name=model_name,
        current_time=datetime.utcnow())  

@main.route('/identify', methods=['GET', 'POST'])
def identify(): 
    return render_template('identify.html')  

@main.route('/diagnose', methods=['GET', 'POST'])
def diagnose(): 
    return render_template('diagnose.html')  