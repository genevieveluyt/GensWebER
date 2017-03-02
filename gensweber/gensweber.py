from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from flask_pymongo import PyMongo
# from flask.ext.pymongo import PyMongo
import os
import sqlite3
import mysql.connector

from db_interface import db_interface
import schema_algs

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , gensweber.py

# Load default config and override config from an environment variable
app.config.update(dict(
    #DATABASE=os.path.join(app.root_path, 'gensweber.db'),
    MONGO_DBNAME='gensweber',
    SECRET_KEY='development key'
))
app.config.from_envvar('GENSWEBER_SETTINGS', silent=True)

db = None
with app.app_context():
    db = db_interface(app)


@app.route("/", methods=['GET', 'POST'])
def dashboard():
    username = session.get('logged_in_username')
    if not username:
        return redirect(url_for('login'))

    # If user added a new project or edited the name of an existing one
    if request.method == 'POST':
        print('POST')
        print(request.form)
        old_name = request.form.get('old_name', None)
        if old_name:
            db.update_project_name(username, old_name, new_name)
        else:
            project_name = request.form['project_name']
            db_name = request.form['db_name']
            db_user = request.form['username']
            db_pass = request.form['password']
            host = request.form['host']
            port = request.form['port']

            abstract_schema = schema_algs.get_abstract_schema(db_name, db_user, db_pass, host, port)
            db.create_project(username, project_name, db_name, db_user, db_pass, host, port, abstract_schema)

    projects = db.get_projects(username)

    return render_template('dashboard.html', projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.validate_login(username, password):
            # Successfully logged in
            session['logged_in_username'] = username
            return redirect(url_for('dashboard'))
        elif not db.user_exists(username):
            # username not found in db
            error = "That username doesn't exist!"
        else:
            # username exists but login failed so must be incorrect password
            error = 'Invalid password'
    return render_template('login.html', error=error) 

@app.route('/new_account', methods=['GET', 'POST'])
def new_account():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.user_exists(username):
            error = 'Username taken'
        elif request.form['password'] == '':
            error = 'Please choose a password'
        else:
            db.create_user(username, password)
            session['logged_in_username'] = username
            return redirect(url_for('dashboard')) 
    # Uses the same template as login
    # Changes from login are determined by the url in the template itself
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in_username', None)
    return redirect(url_for('login'))

@app.route('/<project_id>', methods=['GET', 'POST', 'DELETE'])
def abstract_diagram(project_id):
    username = session.get('logged_in_username')
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # TODO update name/position/visibility data
        # no need to reload the page since Go.js updates the UI live
        return
    elif request.method == 'DELETE':
        db.delete_project(username, project_id)
        return redirect(url_for('dashboard')) 

    project_name = db.get_project_details(username, project_id).get('name')
    abstract_schema = db.get_abstract_schema(username, project_id)

    return render_template('abstract_diagram.html', project_name=project_name, abstract_schema=abstract_schema)

@app.route('/<project_id>/<entity_id>', methods=['GET', 'POST'])
def abstract_entity(project_id, entity_id):
    username = session.get('logged_in_username')
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # TODO update position/visibility data
        # no need to reload the page since Go.js updates the UI live
        return

    entity_schema = db.get_abstract_entity(username, project_id, entity_id)

    return render_template('abstract_entity.html', entity_schema=entity_schema)

# TODO project information will be passed in instead of this being a route
@app.route("/dbSchema",methods=['GET','POST'])
def reSchema():
    reDic = request.json
    print(reDic)
    schema = jsonify(schema_algs.get_db_schema(reDic['user'],reDic['name'],reDic['password'],reDic['host']))
    return(schema)
