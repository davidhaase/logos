from datetime import datetime

from . import db

### To load look-up tables
# (venv) $ flask shell
# >>> from logos import db
# >>> from app import data_loader as ld
# >>> ld.load_data(db, Language, TranslationModel)
# '1 français'
# '2 english'
# '3 español'
# '4 türkçe'
# '5 italiano'
# '6 deutsch'


class Translation(db.Model):
    __tablename__ = 'translations'
    id = db.Column(db.Integer, primary_key=True)
    source_txt = db.Column(db.String(64), index=True)
    target_txt = db.Column(db.String(64), index=True)
    model_id = db.Column(db.Integer, db.ForeignKey('translation_models.id'))

    def __repr__(self):
        return '<Translation %r>' % self.input

class TranslationModel(db.Model):
    __tablename__ = 'translation_models'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    name = db.Column(db.String(64), unique=True)
    source_lang_id = db.Column(db.Integer, db.ForeignKey('languages.id'))
    target_lang_id = db.Column(db.Integer, db.ForeignKey('languages.id'))
    translations = db.relationship('Translation', foreign_keys=[Translation.model_id], lazy='dynamic')
    training_id = db.Column(db.Integer, db.ForeignKey('training_sets.id'))
    build_id = db.Column(db.Integer, db.ForeignKey('build_versions.id'))

    def __repr__(self):
        return '<TranslationModel %r>' % self.name

class TrainingSet(db.Model):
    __tablename__ = 'training_sets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    summary = db.Column(db.String(64))
    number_of_epochs = db.Column(db.Integer, db.ForeignKey('epochs.id'))
    number_of_sentences = db.Column(db.Integer, db.ForeignKey('subsets.id'))
    build_id = db.Column(db.Integer, db.ForeignKey('build_versions.id'))

class BuildVersion(db.Model):
    __tablename__ = 'build_versions'
    id = db.Column(db.Integer, primary_key=True)
    version_num = db.Column(db.String(64), unique=True)
    summary = db.Column(db.String(64))

    def __repr__(self):
        return '<BuildVersion %r>' % self.number_of_sentences


# Look-Up Tables
class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    en_name = db.Column (db.String(64))
    source_langs = db.relationship('TranslationModel', foreign_keys=[TranslationModel.source_lang_id], lazy='dynamic')
    target_langs = db.relationship('TranslationModel', foreign_keys=[TranslationModel.target_lang_id], lazy='dynamic')
    is_source_lang = db.Column(db.Boolean, default=False)
    is_target_lang = db.Column (db.Boolean, default=False)

    def __repr__(self):
        return '<Language %r>' % self.name

class Epoch(db.Model):
    __tablename__ = 'epochs'
    id = db.Column(db.Integer, primary_key=True)
    number_of_epochs = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return '<Epoch %r>' % self.number_of_epochs

class Subset(db.Model):
    __tablename__ = 'subsets'
    id = db.Column(db.Integer, primary_key=True)
    number_of_sentences = db.Column(db.Integer, unique=True)
    display_string_of_number = db.Column(db.String(64))

    def __repr__(self):
        return '<Subset %r>' % self.number_of_sentences



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
