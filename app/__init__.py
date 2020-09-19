"""
The APP PACKAGE CONSTRUCTOR
Delay the creation of the application by moving it into a factory function
that can be explicitly invoked from the script. This not only gives the script
time to set the configuration, but also the ability to create multiple
application instances—another thing that can be very useful during testing

This constructor imports most of the Flask extensions currently in use, but
because there is no application instance to initialize them with, it creates
them uninitialized by passing no arguments into their constructors. The
create_app() function is the application factory, which takes as an argument
the name of a configuration to use for the application. The configuration
settings stored in one of the classes defined in config.py can be imported
directly into the application using the from_object() method available in
Flask’s app.config configuration object. -- Miguel Grinberg: Flask Web Development"""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
