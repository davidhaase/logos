class Translator():
    language = 'French'

    def __repr__(self):
        return '<Translator %r>' % self.language

    def translate(self, source):
        return 'TRANSLATED TEXT (' + source + ')'
