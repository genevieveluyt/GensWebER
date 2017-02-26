#Milestone 1: Gen's Web-ER

##DEV Instructions

###Setup
1. Install this Python package
In the root directory:
`$ pip install --editable .`

2. Initialize the database
`$ flask initdb`

####Optional: Install SQLite
(If you want to be able to make db queries through the command line like mysql)
`$ sudo apt-get install sqlite3`

Activate the database to use it
`$ sqlite3 gensweber/gensweber.db`

View tables
`$ .tables`

View table schema (columns)
`$ .schema TABLENAME`

###Running the application
In the root directory:
`
$ export FLASK_APP=gensweber
$ export FLASK_DEBUG=true
$ PYTHONPATH=<path to app root folder> flask run
`

##Instructions

1. Make sure Python 2 is installed

2. Install this Python package
In the root directory:
`$ pip install .`

3. Initialize the database
`$ flask initdb`

4. Run the application
`
$ export FLASK_APP=gensweber
$ PYTHONPATH=<path to app root folder> flask run
`


`