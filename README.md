# logos
Web interface in Python Flask that allows users to enter text and get translations.
## Version History
### Release v0.1
#### Release Notes
- This version is simply a proof of concept for building a localhost website in python Flask.  Once downloaded and set up, it will run on localhost:5000.
- The homepage will allow you to enter text and click Submit
- The machine-translation models are not hooked up in this version, but a simple placeholder transformation of the entered text is echoed back to the page.
- Placeholder ipsum lorem text appears in navigation tabs
#### Runbook: How to run this on your own localhost
1. Clone this repository to your local drive
2. Create the virtual environment from the top level, *logos*, upgrade the pip installer, pip install the *requirements.txt* and activate the environment
    $ python3 -m venv ./venv
    $ pip install --upgrade pip
    $ pip install -r requirements.txt
    $ source venv/bin/activate


