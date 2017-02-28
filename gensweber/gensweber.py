from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import os
import sqlite3
import mysql.connector

import db_interface
import schema_algs

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , gensweber.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'gensweber.db'),
    SECRET_KEY='development key',
))
app.config.from_envvar('GENSWEBER_SETTINGS', silent=True)


# So that you can run 'flask initdb' from the command line
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/", methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in_username'):
        return redirect(url_for('login'))

    # If user added a new project or edited the name of an existing one
    # if request.method == 'POST':
        # TODO If there is a project ID, update the name of an existing project

        # Otherwise, add the new project to the user's account and get the schemas

    # TODO get projects from user's account
    projects = None

    return render_template('dashboard.html', projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db_interface.validate_login(get_db(), username, password):
            # Successfully logged in
            session['logged_in_username'] = username
            return redirect(url_for('dashboard'))
        elif not db_interface.user_exists(get_db(), username):
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
        if db_interface.user_exists(get_db(), username):
            error = 'Username taken'
        elif request.form['password'] == '':
            error = 'Please choose a password'
        else:
            db_interface.create_user(get_db(), username, password)
            print('users:', db_interface.query_db(get_db(), 'select * from users'))
            session['logged_in_username'] = username
            return redirect(url_for('dashboard')) 
    # Uses the same template as login
    # Changes from login are determined by the url in the template itself
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in_username', None)
    return redirect(url_for('login'))

@app.route('/<project_id>', methods=['GET', 'POST'])
def abstract_diagram(project_id):
    if not session.get('logged_in_username'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # TODO update name/position/visibility data
        # no need to reload the page since Go.js updates the UI live
        return

    # TODO get abstract schema data (including positions and visibility data) from user's account
    # For each entity, add name by doing queries using the key value (as id)
    data = None

    return render_template('abstract_diagram.html', data=data)

@app.route('/<project_id>/<entity_id>', methods=['GET', 'POST'])
def abstract_entity(project_id, entity_id):
    if not session.get('logged_in_username'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # TODO update position/visibility data
        # no need to reload the page since Go.js updates the UI live
        return

    # TODO get abstract schema data (including positions and visibility data) from user's account
    data = None

    return render_template('abstract_entity.html')

# TODO project information will be passed in instead of this being a route
@app.route("/dbSchema",methods=['GET','POST'])
def reSchema():
    reDic = request.json
    print(reDic)
    schema = jsonify(schema_algs.get_db_schema(reDic['user'],reDic['name'],reDic['password'],reDic['host']))
    return(schema)
