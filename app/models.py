from . import db




class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    en_name = db.Column (db.String(64))
    is_input_lang = db.Column(db.Boolean, default=False)
    is_output_lang = db.Column (db.Boolean, default=False)

    def __repr__(self):
        return '<Language %r>' % self.name

class Translation(db.Model):
    __tablename__ = 'translations'
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.String(64), index=True)
    input_lang_id = db.Column(db.Integer, db.ForeignKey('languages.id'))
    
    output = db.Column(db.String(64))
    output_lang_id = db.Column(db.Integer, db.ForeignKey('languages.id'))

    def __repr__(self):
        return '<Translation %r>' % self.input


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
