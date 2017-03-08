from flask import Flask, session
from flask_pymongo import PyMongo
import json

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
            user = self.db.users.find_one({'username': username})
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
		return projects_array

	def get_project_details(self, username, project_id):
		project = self.db.users.find_one({'username': username}, {'projects.{}'.format(project_id): 1}).get('projects', {}).get(project_id, {})
		project.pop('abstract_schema'.decode('unicode-escape'),None)
                project.pop('abstract_schema', None)
		return project

	def get_abstract_schema(self, username, project_id):
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
					'name': table['name']
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
		return self.db.users.find_one(
			{
				'username': username
			}, 
			{
				'projects.{}.saved_data.abstract_schema'.format(project_id): 1
			}
		).get('projects', {}).get(project_id, {}).get('saved_data', {}).get('abstract_schema', {})

	def get_saved_abstract_entity_data(self, username, project_id, entity_id):
		return self.db.users.find_one(
			{
				'username': username
			}, 
			{
				'projects.{}.saved_data.entities.{}'.format(project_id, entity_id): 1
			}
		).get('projects', {}).get(project_id, {}).get('saved_data', {}).get('entities', {}).get(entity_id, {})

	def get_abstract_entity_name(self, username, project_id, entity_id):
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
