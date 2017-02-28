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