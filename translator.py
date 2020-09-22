__version__ = '0.0.1'
__author__ = 'David Haase'
__copyright__ = 'Copyright (c) David Haase'


class Translator():
    language = 'French'

    def __repr__(self):
        return '<Translator %r>' % self.language

    def translate(self, source):
        return 'TRANSLATED TEXT (' + source + ')'

if __name__ == '__main__':
    print(f'You have entered {__name__}')
    # french = Language(  code='fr',name='français', en_name='French', is_input_lang=False, is_output_lang=True)
    # english = Language(  code='en',name='english', en_name='English', is_input_lang=True, is_output_lang=False)
    # spanish = Language(  code='es',name='español', en_name='Spanish', is_input_lang=False, is_output_lang=True)
    # italian = Language(  code='it',name='italiano', en_name='Italian', is_input_lang=False, is_output_lang=True)
    # german = Language(  code='de',name='deutsch', en_name='German', is_input_lang=False, is_output_lang=True)   
  
    # db.session.add(french)
    # db.session.commit()
