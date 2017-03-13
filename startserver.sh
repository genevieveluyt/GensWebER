#!/bin/bash  

source venv/bin/activate
export FLASK_APP=gensweber
export FLASK_DEBUG=true
PYTHONPATH=${PWD} flask run
