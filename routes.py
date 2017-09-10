import json
from flask import request, session, redirect, url_for, render_template

import gensweber.helpers.schema_algs as schema_algs
from . import app, db


@app.route("/", methods=['GET', 'POST'])
def dashboard():
    username = session.get('logged_in_username')
    if not username:
        return redirect(url_for('login'))

    error = None

    if request.method == 'POST':

        # If user created a new project
        if request.form:
            project_name = request.form['project_name']
            db_name = request.form['db_name']
            db_user = request.form['username']
            db_pass = request.form['password']
            host = request.form['host']
            port = request.form['port']
            java_directory = request.form.get('java_directory', None)     # where to look for foreign key candidates

            db_schema = schema_algs.get_db_schema(db_name, db_user, db_pass, host, port, java_directory)

            if db_schema:
                abstract_schema = db_schema.get('cluster')
                db.create_project(username, project_name, db_name, db_user, db_pass, host, port, abstract_schema)
            else:
                error = 'Unable to connect to {}. Please check your connection details.'.format(db_name)
        else: # Change name of existing project
            old_name = request.json['old_name']
            new_name = request.json['new_name']
            db.update_project_name(username, old_name, new_name)
            return ""

    projects = db.get_projects(username)

    return render_template('dashboard.html.j2', projects=projects, error=error)

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
    return render_template('login.html.j2', error=error) 

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
    return render_template('login.html.j2', error=error)

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
        db.save_abstract_schema(username, project_id, json.dumps(request.json))
        return ""
    elif request.method == 'DELETE':
        db.delete_project(username, project_id)
        return "200"

    project_name = db.get_project_details(username, project_id).get('name')
    diagram_data, entities = db.get_abstract_schema(username, project_id)

    return render_template('abstract_diagram.html.j2', project_name=project_name, diagram_data=diagram_data, entities=entities)

@app.route('/<project_id>/<entity_id>', methods=['GET', 'POST'])
def abstract_entity(project_id, entity_id):
    username = session.get('logged_in_username')
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        db.save_abstract_entity(username, project_id, entity_id, json.dumps(request.json))
        return ""

    entity_name = db.get_abstract_entity_name(username, project_id, entity_id)
    diagram_data, tables = db.get_abstract_entity(username, project_id, entity_id)

    return render_template('abstract_entity.html.j2', entity_name=entity_name, diagram_data=diagram_data, tables=tables, project_id=project_id)
