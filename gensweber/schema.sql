drop table if exists projects;
create table projects (
	id integer primary key autoincrement,
	user_id integer not null,
	name text not null,
	db_name text not null,
	host text not null,
	port integer not null,
	abstract_schema text,
	foreign key(user_id) references users(id)
);

drop table if exists abstract_schemas;
create table abstract_schemas (
	id integer primary key autoincrement,
	project_id integer not null,
	schema text not null,
	foreign key(project_id) references projects(id)
);

drop table if exists abstract_entities;
create table abstract_entities (
	id integer primary key autoincrement,
	project_id integer not null,
	name text not null,
	schema text not null,
	foreign key(project_id) references projects(id)
);

drop table if exists users;
create table users (
	id integer primary key autoincrement,
	username text not null,
	password text not null
);