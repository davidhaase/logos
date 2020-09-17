#########
# BLUEPRINTS
# Blueprints are created by instantiating an object of class Blueprint. The
# constructor for this class takes two required arguments: the blueprint name
# and the module or package where the blueprint is located. As with applications,
# Python’s __name__ variable is in most cases the correct value for the second
# argument.
# The routes of the application are stored in an app/main/views.py module inside
# the package, and the error handlers are in app/main/errors.py. Importing these
# modules causes the routes and error handlers to be associated with the
# blueprint. It is important to note that the modules are imported at the bottom
# of the app/main/__init__.py script to avoid errors due to circular
# dependencies. In this particular example the problem is that app/main/views.py
# and app/main/errors.py in turn are going to import the main blueprint object,
# so the imports are going to fail unless the circular reference occurs after
# main is defined.  -- Miguel Grinberg: Flask Web Development

from flask import Blueprint

main = Blueprint('main', __name__)

# PYTHON Relative Paths
# The from . import <some-module> syntax is used in Python to represent relative
# imports. The . in this statement represents the current package. You are going
# to see another very useful relative import soon that uses the form
#   from .. import <some-module>, where[…]
# -- Miguel Grinberg: Flask Web Development
from . import views, errors
