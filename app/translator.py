__version__ = '0.0.1'
__author__ = 'David Haase'
__copyright__ = 'Copyright (c) David Haase'


class Translator():
    def __init__(self):
        language = 'French'

    def __repr__(self):
        return '<Translator %r>' % self.language

    def translate(self, input, lang):
        return f'{input} translated into {lang}'

if __name__ == '__main__':
    print(f'You have entered {__name__}')
# french = Language(  code='fr',name='français', en_name='French', is_source_lang=False, is_target_lang=True)
# english = Language(  code='en',name='english', en_name='English', is_source_lang=True, is_target_lang=False)
# spanish = Language(  code='es',name='español', en_name='Spanish', is_source_lang=False, is_target_lang=True)
# italian = Language(  code='it',name='italiano', en_name='Italian', is_source_lang=False, is_target_lang=True)
# german = Language(  code='de',name='deutsch', en_name='German', is_source_lang=False, is_target_lang=True)
# turkish = Language( code='tk', name='türkçe', en_name='Turkish', is_source_lang=False, is_target_lang=True) 
# en_2_fr = TranslationModel (name='en_2_fr', source_lang_id=2, target_lang_id=1)
# en_2_es = TranslationModel (name='en_2_es', source_lang_id=2, target_lang_id=3)
# en_2_tk = TranslationModel (name='en_2_tk', source_lang_id=2, target_lang_id=4)
# en_2_it = TranslationModel (name='en_2_it', source_lang_id=2, target_lang_id=5)
# en_2_de = TranslationModel (name='en_2_de', source_lang_id=2, target_lang_id=6)
# db.session.add_all([french, english, spanish, italian, turkish, german, en_2_fr, en_2_es, en_2_tk, en_2_it, en_2_de])
# db.session.commit() 
