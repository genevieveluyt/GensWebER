def user_exists(db, username):
	user = query_db(db, 'select username from users where username = ?', [username], one=True)
	return True if user else False

def create_user(db, username, password):
	query_db(db, 'insert into users (username, password) values (?, ?)', [username, password])

def validate_login(db, username, password):
	user = query_db(db, 'select username from users where username = ? and password = ?', [username, password], one=True)
	return True if user else False

def query_db(db, query, args=(), one=False):
	cur = db.execute(query, args)
	db.commit()
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv