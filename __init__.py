import json
import os
from flask import Flask
from flask_pymongo import PyMongo

from gensweber.helpers.db_interface import db_interface

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY=os.environ['SECRET_KEY'],
    MONGO_URI=os.environ['MONGO_URI'],
    MONGO_DBNAME='gensweber'
))

mongo = PyMongo(app)

with app.app_context():
    db = db_interface(mongo)

from . import routes
