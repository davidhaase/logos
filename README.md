# logos
Python Flask server with a front end that allows users to enter text and get translations.
## Logos Web Server Set-Up
### Runbook: How to run this on your own localhost
1. Clone or download this repository to your local drive. The top folder should be *__logos__*, or *__logos-master__* if you downloaded the zip.
2. Navigate to the logos/bin folder, use Terminal to run the setup script to set up virtual environment and load packages

                $ ./setup.sh

3. Spin up the Flask server by running the run.sh

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
#### v1.0.2 Notes: What's in this release
##### New
- Moved config.py into its own config folder
- Added Docker container functionality (Dockerfile & docker scripts); if you are not using any docker containers, these can be ignored
##### Known Issues
- __DB Crash in Docker Container__.  If you run the website from the Docker container, the browser will crash with a DB error when a novel translation term is entered. A DB read-only error is returned in the browser.  
#### v1.0.0 Notes: What's in this release
- This version is simply a proof of concept for building a localhost website in python Flask.  Once downloaded and set up, it will run on localhost:5000.
- The homepage will allow you to enter text and click Submit
- The machine-translation models are not hooked up in this version, but a simple placeholder transformation of the entered text is echoed back to the page.
- Placeholder ipsum lorem text appears in navigation tabs
