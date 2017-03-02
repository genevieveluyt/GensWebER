from flask import Flask, session
# from flask.ext.pymongo import PyMongo
from flask_pymongo import PyMongo

class db_interface:
	# table names
	USERS_TABLE = 'users'
	PROJECTS_TABLE = 'projects'
	SCHEMAS_TABLE = 'abstract_schemas'
	ENTITIES_TABLE = 'abstract_entities'

	def __init__(self, app):
		self.mongo = PyMongo(app)
		self.db = self.mongo.db

	def user_exists(self, username):
		user = self.get_user_data(username)
		if user:
			print("User tried to make account with username " + username + " but it exists already.")
		return True if user else False

	def create_user(self, username, password):
		self.db.users.insert({
			'username': username,
			'password': password,
			'project_id_counter': 0
		})
		print("Account created for " + username + ".")

	def validate_login(self, username, password):
		user = self.db.users.find_one({
			'username': username,
			'password': password
		})
		return True if user else False

	def create_project(self, username, name, db_name, db_user, db_password, host, port, abstract_schema):
		project_id = self.db.users.find_one({'username': username}, {'project_id_counter': 1})['project_id_counter']
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
		projects = self.db.users.find_one({'username': username}, {'projects':1}).get('projects', {})
		projects_array = []

		for key, value in projects.iteritems():
			value.pop('abstract_schema')
			projects_array.append(value)
		print('Projects: {}'.format(projects_array))
		return projects_array

	def get_project_details(self, username, project_id):
		project = self.db.users.find_one({'username': username}, {'projects.{}'.format(project_id): 1}).get('projects', {}).get(project_id, {})
		project.pop('abstract_schema')
		return project

	def get_abstract_schema(self, username, project_id):
		abstract_schema = self.db.users.find_one({'username': username}, {'projects.{}.abstract_schema'.format(project_id): 1}).get('projects', {}).get(project_id, {}).get('abstract_schema', {})
		
		for entity in abstract_schema.get('entities', []):
			table_names = []
			for table in entity.get('tables', []):
				table_names.append(table['name'])
			entity['tables'] = table_names

		return abstract_schema

	def get_abstract_entity(self, username, project_id, entity_id):
		data = self.db.users.find_one({'username': username}, {'projects.{}.abstract_schema.entities'.format(project_id): {'$slice': [int(entity_id), 1]} })
		print('Getting entity {} for project {}'.format(entity_id, project_id))
		entity = data.get('projects', {}).get(project_id, {}).get('abstract_schema', {}).get('entities', [])[0]
		entity.pop('location')
		entity.pop('expanded')
		entity.pop('visible')
		return entity
