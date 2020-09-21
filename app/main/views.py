from datetime import datetime

from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import Job, Language, InputLanguage, OutputLanguage
from ..email import send_email
from ..translator import Translator
from . import main
from .forms import SourceTxtForm


@main.route('/', methods=['GET', 'POST'])
def index():
    
    form = SourceTxtForm()
    tr = Translator()
    if form.validate_on_submit():
        input = Job.query.filter_by(input=form.form_input.data).first()
        if input is None:
            input = Job(input=form.form_input.data)
            db.session.add(input)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['form_input'] = form.form_input.data
        session['form_output'] = tr.translate(form.form_input.data)
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form,
                           form_output=session.get('form_output'),
                           form_input=session.get('form_input'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())

@main.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@main.route('/themodels', methods=['GET', 'POST'])
def themodels():
    return render_template('themodels.html')
