import os
from datetime import datetime
from decimal import Decimal
import json
import pickle
import re

from flask import render_template, session, redirect, url_for, current_app, flash
from flask_paginate import Pagination, get_page_args
from .. import config
from .. import logging

from . import main
from .forms import TranslationForm, BuildModelForm, PopulateTablesForm

from ..dynamo import Translation, Language, Model, Engine
from ..translator import Translator
from ..utils import S3File, seconds_to_string


@main.route('/', methods=['GET', 'POST'])
def index():
    # LOAD VARIABLES for the PAGE in GENERAL
    # Display a table of all the translations made so far
    Translations = Translation()

    # LOAD VARIABLES for the FORM
    # Query the TranstionModel table to determine which languages are available as source and target
    # Populate the user options based on these availabilities
    form = TranslationForm()
    Models = Model()
    form.form_selection_build.choices = Models.get_distinct('build_display_name')
    form.form_selection_input_lang.choices = Models.get_distinct('source_lang_en')
    form.form_selection_output_lang.choices =Models.get_distinct('target_lang_en')

    
    
    # USER CLICKS SUBMIT (FORM EVENT) - Build a new record and add it to the Translation table
    if form.validate_on_submit():

        # Start a timer to see how long it takes to translate
        start_time = datetime.utcnow()

        # USER DATA FROM FORM
        # The code below converts user-choices into system values
        # Unpack the user-chosen values
        build_display_name = form.form_selection_build.data
        (engine, subset, epochs) = build_display_name.split(' ')
        input_string = form.form_string_input.data
        source_lang_en = form.form_selection_input_lang.data
        target_lang_en = form.form_selection_output_lang.data
        output_string = ''
        
        # Model names are unique by concatenating the model attributes
        name = f'{engine}_{subset}_{epochs}_{source_lang_en}_{target_lang_en}'
        model = Models.get_model(name)
        
        if model:
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
                        'build_display_name' : build_display_name,
                        'input_string' : input_string,
                        'source_lang_en' : source_lang_en,
                        'output_string' : output_string,
                        'target_lang_en' : target_lang_en,
                        'duration' : seconds_to_string(elapsed_time.seconds),
                        'date_created' : date.strftime("%m/%d/%Y, %H:%M:%S")
                    }
                    response = translation.put_item(translation_record)
                    if response:
                        flash(f'Novel translation added: {output_string}')

                except Exception as e:
                    flash(f'Error: not able to add translation to database; {e}') 
            
            # # The translation already exists for this model so used the cached version
            else:
                session['known'] = True
                flash(f'Showing cached translation which already exists in the database')
                output_string = already_translated['output_string']
        
        else: # BIG ERROR, model was not found
            flash(f'Unable to locate model: {name}')
            logging.warning(f'User-selected model name not found: {name}')

        # SAVE BROWSER SESSION
        # (NB: this is NOT the db session)
        session['build_display_name'] = build_display_name
        session['input_string'] = input_string
        session['source_lang_en'] = source_lang_en
        session['target_lang_en'] = target_lang_en
        session['output_string'] = output_string
        
        return redirect(url_for('.index'))
    
    # MAKE FORM PERSISTENT with BROWSER SESSION VARIABLES
    # Make the selected form values persistent after each translation by resetting the form
    # ...to the values in the session[] dictionary
    # But the session keys won't exist if it's the first session of the browser, so
    # ...you can set the default values here for a fresh session
    if 'build_display_name' in session:
       form.form_selection_build.data = session['build_display_name']
    if 'input_string' in session:
        form.form_string_input.data= session['input_string'] 
    if 'source_lang_en' in session:
        form.form_selection_input_lang.data = session['source_lang_en'] 
    else:
        session['source_lang_en'] =form.form_selection_input_lang.choices[0]
    if 'output_string' not in session:
        session['output_string'] = ' '
    
    if 'target_lang_en' in session:
        form.form_selection_output_lang.data= session['target_lang_en'] 
    else:
        session['target_lang_en'] =form.form_selection_output_lang.choices[0]
        
        

        
        
    return render_template(
        'index.html',
        form=form,
        output_string=session.get('output_string'),
        input_string=session.get('input_string'), 
        ouput_selection=session.get('target_lang_en'),
        input_selection=session.get('source_lang_en'),             
        known=session.get('known', False),
        current_time=datetime.utcnow()
    )

@main.route('/modelsummary', methods=['GET', 'POST'])
def summarize_models():
    
    # LOAD VARIABLES for the PAGE in GENERAL
    # Display a table of all the translations made so far
    Models = Model()
    all_models = {}
    for model in Models.scan():
        if model['build_display_name'] not in all_models:
            engine = model['engine']
            training_params = f'{model["subset"]}K {model["epochs"]}e'
            all_models[model['build_display_name']] = {
                'engine' : engine,
                'training_params' : training_params,
                'details' : {}

            }

        languages = f'{model["source_lang_en"]} -> {model["target_lang_en"]}'
        bleus = model['BLEUs']
        date_created = datetime.strptime(model['date_created'], "%m/%d/%Y, %H:%M:%S")

        if languages not in all_models[model['build_display_name']]['details']:
            all_models[model['build_display_name']]['details'][languages] = {'bleus':bleus, 'date_created' : date_created}


    # table_of_model_history = [
    #     [   model['model_name'],
    #         model['engine'],
    #         model['subset'],
    #         model['epochs'],
    #         model['source_lang_en'],
    #         model['target_lang_en'],
    #         datetime.strptime(model['date_created'], "%m/%d/%Y, %H:%M:%S")
    #     ]
    #     for model in Models.scan()
    # ]
    return render_template(
        'modelsummary.html',
        all_models=all_models,
        current_time=datetime.utcnow()
    )


@main.route('/about', methods=['GET', 'POST'])
def about():
    form = PopulateTablesForm()

    if form.validate_on_submit():
        
        # BUILD LANGUAGE TABLE in AWS
        # One-time code to build language table from json file in json dir
        Languages = Language()
        json_file = current_app.config['APP_DIR'] + '/build/json/languagedata.json'
         
        with open(json_file) as json_file:
            language_list = json.load(json_file)
        Languages.load_items(language_list)

        # BUILD ENGINE TABLE in AWS
        # One-time code to populate Engine table 
        filepath = '/Users/davidhaase/Documents/Learn/Flatiron/Projects/machine-translator/translator.py'
        f = open(filepath,'r')
        engine_code = f.read()
        engine_record = {
            'engine_name' : 'devX',
            'engine_code' : engine_code}
        Engines = Engine()
        Engines.put_item(engine_record)

        # BUILD MODEL TABLE in AWS
        # This is one-time code to rebuild the model table from what it finds on S3
        # Crawls S3 to see what models are there and derives the tables values from the structure
        Models = Model()
        s3_dir = S3File('logos-models', 'data')
        relative_path = 'data/models/'
        list_of_models = s3_dir.crawl_models('data/models')
        for engine in list_of_models:
            for build in list_of_models[engine]:
                for source in list_of_models[engine][build]:
                    for target in list_of_models[engine][build][source]:
                        path = f'{relative_path}{engine}/{build}/{source}/{target}/'
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
                        target_pkl = f'{app_dir}/build/model_prefs.pkl'
                        s3_pkl = f'{path}pickles/model_prefs.pkl'
                        
                        pickled_file = S3File('logos-models', s3_pkl)
                        pickled_file.copy_from_S3_to(target_pkl)
                        model_prefs = pickle.load(open(target_pkl, 'rb'))
                        
                        ### End hacks
                        date = datetime.utcnow()
                        
                        model_record = { 
                            'model_name' : f'{engine}_{str(sentences)}K_{str(epochs)}e_{source}_{target}',
                            'build_display_name': f'{engine} {str(sentences)}K {str(epochs)}e',
                            'build' : build,
                            'engine' : engine,
                            'source_lang_en' : source,
                            'target_lang_en' : target,
                            'epochs' : epochs,
                            'subset' : sentences,
                            'date_created' : date.strftime("%m/%d/%Y, %H:%M:%S"),
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
                            },
                            'BLEUs' : {
                                'BLEU1': Decimal(str(model_prefs['BLEU1'])),
                                'BLEU2': Decimal(str(model_prefs['BLEU2'])),
                                'BLEU3': Decimal(str(model_prefs['BLEU3'])),
                                'BLEU4': Decimal(str(model_prefs['BLEU4']))
                            }                           
                        }

                        try:
                            response = Models.put_item(model_record)
                            flash(f'Database tables loaded successfully') 
                        except Exception as e:
                            flash(f'unable to load db: {e}') 
        return redirect(url_for('.about'))

    return render_template('about.html', form=form)  


@main.route('/translationhistory', methods=['GET'])
def translationhistory():
    # This page simply shows a table of all existing translations made by Logos
    # DATABASE: pull a list of all the tranlsations
    Translations = Translation()
    all_translations = [
        [   datetime.strptime(translation['date_created'], "%m/%d/%Y, %H:%M:%S"),
            translation['input_string'],
            translation['source_lang_en'],
            translation['output_string'],
            translation['target_lang_en'],
            translation['build_display_name'],
            translation['duration']
        ]
        for translation in Translations.scan()
    ]

    # SORT
    # Sort the list in descending order of data; i.e., newest first, oldest last
    newest_first = sorted(all_translations, key = lambda x: x[0], reverse=True)

    # PAGINATION
    # Break the tables up, so far, this only defaults to 10 per page
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(newest_first)
    pagination_translations = newest_first[offset: offset + per_page]
    pagination = Pagination(
        page=page, 
        per_page=per_page, 
        total=total,
        css_framework='bootstrap3')
    
    return render_template(
        'translationhistory.html',
        # table_of_translation_history=table_of_translation_history,
        table_of_translation_history=pagination_translations,
        page=page,
        per_page=per_page,
        pagination=pagination,
        current_time=datetime.utcnow())
    
@main.route('/themodels/<engine_name>', methods=['GET', 'POST'])
def enginedetail(engine_name): 
    
    Engines = Engine()
    engine = Engines.get_engine(engine_name)
    return render_template(
        'enginedetail.html',
        engine_code=engine['engine_code'],
        model_name=engine_name,
        current_time=datetime.utcnow())  

@main.route('/identify', methods=['GET', 'POST'])
def identify(): 
    return render_template('identify.html')  

@main.route('/diagnose', methods=['GET', 'POST'])
def diagnose(): 
    return render_template('diagnose.html')  