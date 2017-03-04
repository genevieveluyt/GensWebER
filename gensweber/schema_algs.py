import mysql.connector

def get_abstract_schema(db_name, db_user, db_pass, host, port):
    fake_schema = {
        'entities': [
            {
                'entity_id': 0,
                'name': "AE1",
                'tables': [
                    {
                        'table_id': 0,
                        'name': "TABLE 1",
                        'primary_keys': [ "Dog" ],
                        'attributes': [ "Siberian", "Shiba Inu" ]
                    },
                    {
                        'table_id': 1,
                        'name': 'TABLE 2',
                        'primary_keys': [ "Cat" ],
                        'attributes': [ "Persian", "Ragdoll" ]
                    }

                ],
                'relationships': [
                    {
                        'from': 0,
                        'to': 1
                    }
                ]
            },
            {
                'entity_id': 1,
                'name': "AR1",
                'shape': "Triangle",
                'tables': [
                    {
                        'table_id': 2,
                        'name': "TABLE 3",
                        'primary_keys': [ "Bunny" ],
                        'attributes': [ "Holland Lop", "Angora" ]
                    },
                    {
                        'table_id': 3,
                        'name': 'TABLE 4',
                        'primary_keys': [ "Bear" ],
                        'attributes': [ "Brown", "Polar", "Black" ]
                    },
                    {
                        'table_id': 4,
                        'name': 'TABLE 5',
                        'primary_keys': [ "Wolf" ],
                        'attributes': [ "Timber", "Grey" ]
                    }
                ],
                'relationships': [
                    {
                        'from': 2,
                        'to': 3
                    },
                    {
                        'from': 2,
                        'to': 4
                    }
                ]
            }
        ],
        'relationships': [
            {
                'from': 0,
                'to': 1
            }
        ]
    }
    return fake_schema

def get_db_schema(u,d,p,h):
    print([u,d,p,h])
    cnx = mysql.connector.connect(user=u, database=d, password=p,host=h)
    allTabsCurs = cnx.cursor()
    allTabsCurs.execute("show tables")
    tableNames = allTabsCurs.fetchall()
    allTabsCurs.execute("select * from information_schema.referential_constraints where constraint_schema = '"+ d +"';")
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