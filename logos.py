import os
import click
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

"""Adding the method below allows you to interact with the db models from the
   command-line using the "flask shell" command"""
# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, 
#                 Translation=Translation, 
#                 Language=Language,
#                 TranslationModel=TranslationModel,
#                 Build=Build, 
#                 Epoch=Epoch, 
#                 Subset=Subset)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
