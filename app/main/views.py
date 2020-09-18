from datetime import datetime

from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User, Input
from ..email import send_email
from ..translator import Translator
from . import main
from .forms import NameForm, SourceTxtForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = SourceTxtForm()
    tr = Translator()
    if form.validate_on_submit():
        input = Input.query.filter_by(input=form.form_input.data).first()
        if input is None:
            input = Input(input=form.form_input.data)
            db.session.add(input)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['form_input'] = form.form_input.data
        session['output'] = tr.translate(form.form_input.data)
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form,
                           form_output=session.get('output'),
                           form_input=session.get('form_input'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())
# def index():
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None:
#             user = User(username=form.name.data)
#             db.session.add(user)
#             db.session.commit()
#             session['known'] = False
#             if current_app.config['FLASKY_ADMIN']:
#                 send_email(current_app.config['FLASKY_ADMIN'], 'New User',
#                            'mail/new_user', user=user)
#         else:
#             session['known'] = True
#         session['name'] = form.name.data
#         return redirect(url_for('.index'))
#     return render_template('index.html',
#                            form=form, name=session.get('name'),
#                            known=session.get('known', False),
#                            current_time=datetime.utcnow())

@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@main.route('/themodels', methods=['GET', 'POST'])
def themodels():
    return render_template('themodels.html')
