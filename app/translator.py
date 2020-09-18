__version__ = '0.0.1'
__author__ = 'David Haase'
__copyright__ = 'Copyright (c) David Haase'

class Translator():
    language = 'French'

    def __repr__(self):
        return '<Translator %r>' % self.language

    def translate(self, source):
        return 'TRANSLATED TEXT (' + source + ')'
