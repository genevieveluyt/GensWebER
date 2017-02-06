import datetime
from flask import Flask
from flask import jsonify
from flask import request
from flask import send_from_directory
import mysql.connector
import time
import os
import re


app = Flask(__name__,static_folder=os.path.abspath(os.getcwd()+'/client/html/'))

@app.route("/")
def hello():
    return send_from_directory(app.static_folder,'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder,filename)

@app.route("/dbSchema",methods=['GET','POST'])
def reSchema():
    print('REQUEST.JSON')
    reDic = request.json
    schema = jsonify(getDBschema(reDic['user'],reDic['name'],reDic['password'],reDic['host']))
    return(schema)

def getDBschema(u,d,p,h):
    cnx = mysql.connector.connect(user=u, database=d, password=p,host=h)
    allTabsCurs = cnx.cursor()
    allTabsCurs.execute("show tables")
    tableNames = allTabsCurs.fetchall()
    allTabsCurs.execute("select * from information_schema.referential_constraints where constraint_schema = 'northwind';")
    fkNames = allTabsCurs.fetchall()
    data = {}
    tables = []
    relationships = []
    for table in tableNames:
        currTab = {}
        allTabsCurs.execute("describe "+table[0])
        colInfo = allTabsCurs.fetchall()
        cols = []
        for col in colInfo:
            cols = cols + [col[0]]
        tables.append({"name":table[0],'attributes':cols})
    data['tables'] = tables

    for n in fkNames:
        relationships.append({'from':n[-2],'to':n[-1]})
    data['relationships'] = relationships

    cnx.close()
    return(data)




if __name__ == "__main__":
    app.run()
