# Gen's Web-ER
Visualize the database schema of any online database as a high-level abstract entity-relationship (ER) diagram.

## Setup
This only needs to be done once
1. Install MongoDB Community Edition
2. Install MySQL
3. Clone this repo
```
git clone https://github.com/genevieveluyt/GensWebER.git
```
4. Navigate into the project
```
cd GensWebER
```
5. (Optional but recommended) Create a virtual environment with Python 3
6. Install the Python dependencies
```
pip install -r requirements.txt
```

## Running the Application
1. Start the MongoDB server
2. Start the MySQL service
3. Run the application
```
export FLASK_APP=app.py
flask run
```
4. Navigate to http://localhost:5000 or http://127.0.0.1:5000 in a browser. Works best on Firefox (V45 or higher) or Google Chrome (V49.0 or higher).
