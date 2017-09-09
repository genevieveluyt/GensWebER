import json
import os
from flask import Flask
from flask_pymongo import PyMongo

from gensweber.helpers.db_interface import db_interface

app = Flask(__name__)

app.config.update(dict(
    MONGO_DBNAME='gensweber',
    SECRET_KEY=os.environ.get('MONGO_SECRET_KEY', 'development key')
))

mongo = PyMongo(app)

with app.app_context():
    db = db_interface(mongo)

from . import routes
