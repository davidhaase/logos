# logos
Web interface in Python Flask that allows users to enter text and get translations.
## Version History
### Release v0.1
#### Release Notes: What's in this release
- This version is simply a proof of concept for building a localhost website in python Flask.  Once downloaded and set up, it will run on localhost:5000.
- The homepage will allow you to enter text and click Submit
- The machine-translation models are not hooked up in this version, but a simple placeholder transformation of the entered text is echoed back to the page.
- Placeholder ipsum lorem text appears in navigation tabs
#### Runbook: How to run this on your own localhost
##### Set up the virtual environment
1. Clone this repository to your local drive. The top folder should be *__logos__*.
2. Create the virtual environment from the top level...
3. Upgrade the pip installer...
4. Pip install the *requirements.txt*...
5. And finally, activate the environment:

                $ python3 -m venv ./venv
                $ pip install --upgrade pip
                $ pip install -r requirements.txt
                $ source venv/bin/activate
                
##### Confirm the databases are running
Confirm the database is set up by launching the Flask shell, and typing any of the database objects. You should first set the minimal enivornment variables:
                
                (venv) $ FLASK_APP=logos.py
                (venv) $ FLASK_DEBUG=1
                (venv) $ Flask shell
                >>> app
                <Flask 'app'>
                >>> db
                <<SQLAlchemy engine=sqlite:////Users/.../logos/data-dev.sqlite>'>
                >>> Input
                <<class 'app.models.Input'>>

#### Spin up the Flask server
1. Simply run the run.sh

                (venv) $ run.sh
                
2. Confirm that the Flask server is running and get the URL from the terminal window.  It should look like this:

                 * Serving Flask app "logos.py" (lazy loading)
                 * Environment: production
                   WARNING: This is a development server. Do not use it in a production deployment.
                   Use a production WSGI server instead.
                 * Debug mode: on
                 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
                 * Restarting with static
                 * Debugger is active!
                 * Debugger PIN: 103-549-827

3. Launch a browser to the assigned URL 
