import json
import os
from flask import Flask
from flask_pymongo import PyMongo

from gensweber.helpers.db_interface import db_interface

app = Flask(__name__)

app.config.update(dict(
    # Don't set a default secret key, don't want to accidentally forget to set it
    # in a production environment and have it use the default silently
    SECRET_KEY=os.environ.get('SECRET_KEY'),
    MONGO_URL=os.environ.get('MONGO_URL', 'mongodb://localhost:27017'),
    MONGO_DBNAME='gensweber'
))

mongo = PyMongo(app)

with app.app_context():
    db = db_interface(mongo)

from . import routes
