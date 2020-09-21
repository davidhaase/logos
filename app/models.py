from . import db


class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.String(64))
    output = db.Column(db.String(64))

    def __repr__(self):
        return '<Job %r>' % self.input


class Language (db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    en_name = db.Column(db.String(64))
    input_languages = db.relationship('InputLanguage', backref='role', lazy='dynamic')
    output_languages = db.relationship('OutputLanguage', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Language %r>' % self.en_name

class InputLanguage(db.Model):
    __tablename__ = 'input_languages'
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'))

    def __repr__(self):
        return '<InputLanguages>'

class OutputLanguage(db.Model):
    __tablename__ = 'output_languages'
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'))

    def __repr__(self):
        return '<OutputLanguages>'


# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     users = db.relationship('User', backref='role', lazy='dynamic')
#
#     def __repr__(self):
#         return '<Role %r>' % self.name
#
#
# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
#
#     def __repr__(self):
#         return '<User %r>' % self.username
