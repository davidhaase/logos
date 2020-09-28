import pickle
import string
import re

import numpy as np

from unicodedata2 import normalize

from keras.backend import clear_session
from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

def clean_line(line):
    table = str.maketrans('', '', string.punctuation)
    re_print = re.compile('[^%s]' % re.escape(string.printable))

    line = normalize('NFD', line).encode('ascii', 'ignore')
    line = line.decode('UTF-8')
    # tokenize on white space
    line = line.split()
    # convert to lowercase
    line = [word.lower() for word in line]
    # remove punctuation from each token
    line = [word.translate(table) for word in line]
    # remove non-printable chars form each token
    line = [re_print.sub('', w) for w in line]
    # remove tokens with numbers in them
    line = [word for word in line if word.isalpha()]
    # store as string
    return ' '.join(line)

def encode_lines(tokenizer, max_length, lines):
    # line = np.array([clean_line(line)])
    # integer encode sequences
    lines = tokenizer.texts_to_sequences(lines)
    # pad sequences with 0 values
    lines = pad_sequences(lines, maxlen=max_length, padding='post')
    return lines

class Translator():
    def __repr__(self):
        return '<Translator>'

    def __init__(self):
        try:
            pickle_path = '/Users/davidhaase/Documents/Projects/logos/app/data/models/de_to_en/basic_75K_35E_fixed/pickles/model_prefs.pkl'
            model_prefs = pickle.load(open(pickle_path, 'rb'))
            model_path = '/Users/davidhaase/Documents/Projects/logos/app/data/models/de_to_en/basic_75K_35E_fixed/model.h5'
            self.preferences = model_prefs
            #dict.preferences = {'model_path': '',
            #                   'source_tokenizer': keras_obj,
            #                   'source_max_length': int,
            #                   'source_word_count': int,
            #                   'target_tokenizer': keras_obj,
            #                   'target_word_count': int,
            #                   'target_max_length': int }
            # print(self.preferences['model_path'])
            self.model = load_model(model_path)
            print(self.preferences['source_tokenizer'])
            self.input_text = None

        except Exception as e:
            print(e)

    def word_for_id(self, integer, tokenizer):
        for word, index in tokenizer.word_index.items():
            if index == integer:
                return word
        return None

    def translate(self, line):
        self.input_text = line
        tokenizer = self.preferences['source_tokenizer']
        maxlen = self.preferences['source_max_length']
        encoded_line = encode_lines(tokenizer, maxlen, np.array([clean_line(line)]))
        prediction = self.model.predict(encoded_line, verbose=0)[0]
        integers = [np.argmax(vector) for vector in prediction]
        target = list()
        for i in integers:
            word = self.word_for_id(i, self.preferences['target_tokenizer'])
            if word is None:
                break
            target.append(word)
        return ' '.join(target)
    
    def translate_placeholder(self, input, lang, path_to_model):
        # return f'{input} translated into {lang} using {path_to_model}'

        model_path = '/Users/davidhaase/Documents/Projects/logos/app/data/models/de_to_en/basic_75K_35E_fixed/model.h5'
        
        try:
            self.preferences = model_prefs
            #dict.preferences = {'model_path': '',
            #                   'source_tokenizer': keras_obj,
            #                   'source_max_length': int,
            #                   'source_word_count': int,
            #                   'target_tokenizer': keras_obj,
            #                   'target_word_count': int,
            #                   'target_max_length': int }
            print(self.preferences['model_path'])
            self.model = load_model(self.preferences['model_path'])
            self.input_text = None

        except Exception as e:
            print(e)

        return 'bonjour, tous!'
    
