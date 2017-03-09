from flask import Flask, session
from flask_pymongo import PyMongo
import json

class db_interface:
	def __init__(self, app):
		"""Setup the database connection and keep a reference to it."""
		self.mongo = PyMongo(app)
		self.db = self.mongo.db

	def user_exists(self, username):
		"""Return true if an account exists with the given username, else false."""
            user = self.db.users.find_one({'username': username})
            if user:
                print("User tried to make account with username " + username + " but it exists already.")
            return True if user else False

	def create_user(self, username, password):
		"""Create a new account entry with the given username and password."""
		self.db.users.insert({
			'username': username,
			'password': password,
			'project_id_counter': 0
		})
		print("Account created for " + username + ".")

	def validate_login(self, username, password):
		"""Returns true if an account exists with the given username and password, else false."""
		user = self.db.users.find_one({
			'username': username,
			'password': password
		})
		return True if user else False

	def create_project(self, username, name, db_name, db_user, db_password, host, port, abstract_schema):
		"""Create a new project entry in the account with the given username.

		Keyword arguments:
		username -- the username of the account to which the project should be added
		name -- the project name
		db_name -- the name of the MySQL database
		db_user -- the username to use when connecting to the MySQL database
		db_password -- the password to use when connecting to the MySQL database
		host -- the host to use when connecting to the MySQL database
		port -- the port to use when connecting to the MySQL database
		abstract_schema -- a data object representing the high level representation of the MySQL database
		"""
		project_id = self.db.users.find_one(
			{
				'username': username
			},
			{
				'project_id_counter': 1
			}
		)['project_id_counter']

		self.db.users.find_one_and_update(
			{
				'username': username
			},
			{
				'$set': {
					'projects.{}'.format(project_id): {
						'project_id': project_id,
						'name': name,
						'db_name': db_name,
						'db_user': db_user,
						'db_password': db_password,
						'host': host,
						'port': port,
						'abstract_schema': abstract_schema
					}
				},
				'$inc': {
					'project_id_counter': 1
				}
			}
		)

		print('Created project {}.'.format(project_id))

	def delete_project(self, username, project_id):
		"""Deletes a project from the account with the given username."""
		self.db.users.find_one_and_update(
			{
				'username': username
			},
			{
				'$unset': {
					'projects.{}'.format(project_id): ""
				}
			}
		)

		print("Deleted project {}.".format(project_id))

	def update_project_name(self, username, project_id, new_name):
		"""Rename a project in the account with the given username."""
		self.db.users.find_one_and_update(
			{
				'username': username
			},
			{
				'$set': {
					'projects.{}.name'.format(project_id): new_name
				}
			}
		)

	def get_projects(self, username):
		"""Returns an array with project details (project name and MySQL connection parameters) for the account with the given username."""
		projects = self.db.users.find_one(
			{
				'username': username
			},
			{
				'projects':1
			}
		).get('projects', {})

		projects_array = []

		for key, value in projects.iteritems():
			value.pop('abstract_schema')
			projects_array.append(value)

		return projects_array

	def get_project_details(self, username, project_id):
		"""Returns project details (project name and MySQL connection parameters) for the account with the given username."""
		project = self.db.users.find_one(
			{
				'username': username
			},
			{
				'projects.{}'.format(project_id): 1
			}
		).get('projects', {}).get(project_id, {})

		# linux
		project.pop('abstract_schema'.decode('unicode-escape'),None)
		# windows
		project.pop('abstract_schema', None)

		return project

	def get_abstract_schema(self, username, project_id):
		"""Get data for the high-level representation of the database schema for the given project.

		If Go.js diagram data was saved previously, return saved data, otherwise return raw data.
		"""
		saved_data = self.db.users.find_one(
			{
				'username': username
			}, 
			{
				'projects.{}.saved_data.abstract_schema'.format(project_id): 1
			}
		).get('projects', {}).get(project_id, {}).get('saved_data', {}).get('abstract_schema', {})

		if saved_data:
			entities = json.loads(saved_data)['nodeDataArray']
			return saved_data, entities

		abstract_schema = self.db.users.find_one(
			{
				'username': username
			}, 
			{
				'projects.{}.abstract_schema'.format(project_id): 1
			}
		).get('projects', {}).get(project_id, {}).get('abstract_schema', {})
		
		data = dict()
		data['nodes'] = []
		data['links'] = abstract_schema.get('relationships', [])
		for entity in abstract_schema.get('entities', []):
			tables = []
			for table in entity.get('tables', {}):
				tables.append({
					'name': table['name'],
					'visible': True
				})

			node = {
				'key': entity['entity_id'],
				'name': entity.get('name'),
				'visible': True,
				'expanded': True,
				'tables': tables
			}
			if 'shape' in entity:
				node['shape'] = entity['shape']
				
			data['nodes'].append(node)

		return data, data['nodes']

	def save_abstract_schema(self, username, project_id, data):
		"""Save data produced by Go.js that will be used to load the high-level schema representation of the project in the future."""
		self.db.users.find_one_and_update(
			{
				'username': username
			},
			{
				'$set': {
					'projects.{}.saved_data.abstract_schema'.format(project_id): data
				}
			}
		)

	def get_abstract_entity(self, username, project_id, entity_id):
		"""Get data for an abstract entity or abstract relationship in the high-level database representation for the given project.

		If Go.js diagram data was saved previously, return saved data, otherwise return raw data.
		"""
		saved_data = self.get_saved_abstract_entity_data(username, project_id, entity_id)
		if saved_data:
			tables = json.loads(saved_data)['nodeDataArray']
			return saved_data, tables

		entity_setup_data = self.db.users.find_one(
				{
					'username': username
				},
				{
					'projects.{}.abstract_schema.entities'.format(project_id): {'$slice': [int(entity_id), 1]}
				}
			).get('projects', {}).get(project_id, {}).get('abstract_schema', {}).get('entities', [])[0]
		
		data = {
			'nodes': [],
			'links': entity_setup_data.get('relationships', [])
		}

		for table in entity_setup_data.get('tables', []):
			tableData = {
				'key': table['table_id'],
				'name': table['name'],
				'visible': True,
				'expanded': True,
				'primary_keys': [],
				'foreign_keys': [],
				'attributes': []
			}

			for key in ["primary_keys", "foreign_keys", "attributes"]:
				for value in table.get(key, []):
					tableData[key].append({
						'name': value,
						'visible': True
					})

			data['nodes'].append(tableData)

		return data, data['nodes']

	def save_abstract_entity(self, username, project_id, entity_id, data):
		"""Save data produced by Go.js that will be used to load the schema of the abstract entity or abstract relationship of the project in the future."""
		self.db.users.find_one_and_update(
			{
				'username': username
			},
			{
				'$set': {
					'projects.{}.saved_data.entities.{}'.format(project_id, entity_id): data
				}
			}
		)

	def get_saved_abstract_schema_data(self, username, project_id):
		"""Get Go.js saved data for the high-level representation of the project schema."""
		return self.db.users.find_one(
			{
				'username': username
			}, 
			{
				'projects.{}.saved_data.abstract_schema'.format(project_id): 1
			}
		).get('projects', {}).get(project_id, {}).get('saved_data', {}).get('abstract_schema', {})

	def get_saved_abstract_entity_data(self, username, project_id, entity_id):
		"""Get Go.js saved data for the abstract entity or abstract relationship."""
		return self.db.users.find_one(
			{
				'username': username
			}, 
			{
				'projects.{}.saved_data.entities.{}'.format(project_id, entity_id): 1
			}
		).get('projects', {}).get(project_id, {}).get('saved_data', {}).get('entities', {}).get(entity_id, {})
        
	def get_abstract_entity_name(self, username, project_id, entity_id):
		"""Get the name of the given abstract entity or abstract relationship."""
		saved_shema_data = self.get_saved_abstract_schema_data(username, project_id)
		if (saved_shema_data):
			return next((item for item in json.loads(saved_shema_data).get('nodeDataArray', []) if item['key'] == int(entity_id)), {}).get('name')

		entity_setup_data = self.db.users.find_one(
				{
					'username': username
				},
				{
					'projects.{}.abstract_schema.entities'.format(project_id): {'$slice': [int(entity_id), 1]}
				}
			).get('projects', {}).get(project_id, {}).get('abstract_schema', {}).get('entities', [])[0]
		return entity_setup_data.get('name')
