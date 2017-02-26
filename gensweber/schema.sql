drop table if exists projects;
create table projects (
	id integer primary key autoincrement,
	name text not null,
	host text not null,
	port integer not null
);

drop table if exists users;
create table users (
	id integer primary key autoincrement,
	username text not null,
	password text not null
);