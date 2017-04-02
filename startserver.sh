#!/bin/bash  

sudo service mysql start

# create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    virtualenv venv
fi

# activate virtual environment
source venv/bin/activate

# install gensweber as editable package
pip install --editable .

# start flask server
export FLASK_APP=gensweber
export FLASK_DEBUG=true
PYTHONPATH=${PWD} flask run
