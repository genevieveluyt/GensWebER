#Milestone 1: Gen's Web-ER

##DEV Instructions

###Setup

1. Create a virtual environment. We don't want to mess up the Python installation used by the operating system.
```pip install virtualenv```
In the root directory of gensweber:
```virtualenv venv```
This creates a folder called venv which contains a separate Python installation (like how Node uses node_modules).
Activate the environment:
```source venv/bin/activate```
Any packages you install now using pip only exist in this virtual environment. You can tell you're in a virtual environment because the command line prompt starts with `(<virtual environment name>)`, in this case `(venv) oscar14@oscar14-VirtualBox:`
To deactivate the virtual environment when you're done working on the project just type `deactivate`. The virtual environment has to be reactivated every time you open a command line window.

2. Install this Python package and its dependencies in the virtual environment
In the root directory:
```$ pip install --editable .```

3. Initialize the database
```$ flask initdb```

####Optional: Install SQLite
(If you want to be able to make db queries through the command line like mysql for debugging)
```$ sudo apt-get install sqlite3```

Activate the database to use it
```$ sqlite3 gensweber/gensweber.db```

View tables
```$ .tables```

View table schema (columns)
```$ .schema TABLENAME```

###Running the application
Activate the virtual environment if it is not currently active
```source venv/bin/activate```

In the root directory:
```
$ export FLASK_APP=gensweber
$ export FLASK_DEBUG=true
$ PYTHONPATH=<path to app root folder> flask run
```

##Instructions

1. Make sure Python 2 is installed

2. Install this Python package
In the root directory gensweber:
```$ pip install .```

3. Initialize the database
``` flask initdb```

4. Run the application
```
$ export FLASK_APP=gensweber
$ PYTHONPATH=<path to app root folder> flask run
```