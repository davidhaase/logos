# logos
Python Flask server with a front end that allows users to enter text and get translations.
## Logos Web Server Set-Up
### Runbook: How to run this on your own localhost
#### Set up the virtual environment
1. Clone this repository to your local drive. The top folder should be *__logos__*.
2. Create the virtual environment from the top level...
3. Activate the virtual environment
4. Upgrade the pip installer...
5. And finally, pip install the *requirements.txt*...

                $ python3 -m venv ./venv
                $ source venv/bin/activate
                (venv) logos $ pip install --upgrade pip
                (venv) logos $ pip install -r requirements.txt

6. Confirm databases are running, by assigning the environment variable
7. Then, launch the flask shell
8. Type any of the objects; e.g., app, db, Input
9. If you see the response below, you're ready to go so deactivate.

                (venv) logos $ export FLASK_APP=logos.py
                (venv) logos $ flask shell
                >>> app
                <Flask 'app'>
                >>> db
                <<SQLAlchemy engine=sqlite:////Users/.../logos/data-dev.sqlite>'>
                >>> Input
                <<class 'app.models.Input'>>
                >>> exit()
                (venv) logos $ deactivate

10. Spin up the Flask server by running the run.sh

                $ ./run.sh

11. Confirm that the Flask server is running and get the URL from the terminal window.  It should look like this:

                 * Serving Flask app "logos.py" (lazy loading)
                 * Environment: production
                   WARNING: This is a development server. Do not use it in a production deployment.
                   Use a production WSGI server instead.
                 * Debug mode: on
                 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
                 * Restarting with static
                 * Debugger is active!
                 * Debugger PIN: 103-549-827

12. Launch a browser to the assigned URL

## Version History
### Release v1.0
#### Release Notes: What's in this release
- This version is simply a proof of concept for building a localhost website in python Flask.  Once downloaded and set up, it will run on localhost:5000.
- The homepage will allow you to enter text and click Submit
- The machine-translation models are not hooked up in this version, but a simple placeholder transformation of the entered text is echoed back to the page.
- Placeholder ipsum lorem text appears in navigation tabs
