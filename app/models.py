from . import db


class Input(db.Model):
    __tablename__ = 'inputs'
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.String(64), unique=True, index=True)    
    output = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<Input %r>' % self.input



class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
