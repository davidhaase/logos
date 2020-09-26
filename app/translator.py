from keras.backend import clear_session


class Translator():
    def __repr__(self):
        return '<Translator>'

    def translate(self, input, lang, path_to_model):
        return f'{input} translated into {lang} using {path_to_model}'
    
