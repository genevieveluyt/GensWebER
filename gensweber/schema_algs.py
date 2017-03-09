import mysql.connector
import copy

def get_db_schema(d,u,p,h,o):
    """Get data for a high-level representation of a MySQL database schema.

    Keyword arguments:
    d -- MySQL database name
    u -- username that will be used to connect to the MySQL database
    p -- password that will be used to connect to the MySQL database
    h -- host that will be used to connect to the MySQL database
    o -- port that will be used to connect to the MySQL database
    """
    print([u,d,p,h,o])
    #Connect to host
    try:
        cnx = mysql.connector.connect(user=u, database=d, password=p,host=h,port = o)
    except:
        print("Unable to connect to database")
        return None
    #Create a databse curser and use it to fetch all the tables, primary keys, and foreign keys
    allTabsCurs = cnx.cursor()
    allTabsCurs.execute("show tables")
    tableNames = allTabsCurs.fetchall()
    allTabsCurs.execute("select * from information_schema.referential_constraints where constraint_schema = '"+ d +"';")
    fkNames = allTabsCurs.fetchall()
    data = {}
    tables = []
    relationships = []
    #For each table...
    for table in tableNames:
        currTab = {}
        allTabsCurs.execute("describe "+table[0])
        colInfo = allTabsCurs.fetchall()
        cols = []
        pris = []
        #Harvest all the column information
        for col in colInfo:
            cols = cols + [col[0]]
            if col[3]=='PRI':
                pris.append(col[0])
        tables.append({"name":table[0],'attributes':cols,'pks':sorted(pris)})
    #Save all the tables to the return struct
    data['tables'] = tables
	
    #For each foreign key, add the table it's referenced in and the tables it references to the relationships section of the return struct
    for n in fkNames:
        relationships.append({'from':n[-2],'to':n[-1]})
    data['relationships'] = relationships
    #Generate abstract clusters and relationships
    clusters =  ClusterTables(sorted(tables,key=tabKey))
    #Convert the output of ClusterTables into the format used by the front end and add it to the return struct
    data['cluster'] = get_abstract_schema(clusters,tables,relationships)

    #close the database pointer
    cnx.close()
    return(data)

def get_abstract_schema(clusters,tables,relationships):
    """Converts the output from ClusterTables into the format used by the front end.

    Keyword arguments:
    clusters -- abstract entity information produced by running the clustering algorithm
    tables -- database tables
    relationships -- database foreign key relationships
    """
    #save the fields of the structs into local variables
    cluster = clusters['cluster']
    nes = clusters['nes']
    nas = clusters['nas']
    argument = clusters['arg']
    abstract_schema = {'entities':[], 'relationships':[]}
    entities = []
    table_id = 0
    entity_id = 0
    #Foreach abstract entity or relationship...
<<<<<<< HEAD
    for i in range(max(nas+1,len(cluster))):
=======
    for i in range(max(nas,len(cluster))):
>>>>>>> 913108990a7ae2b074499b754e19363dbb91fc96
        #If it's a relationship...
        if i>nes:
            #Add it to the entities list as a triangular abstract relationship bubble
            entity = {'entity_id':entity_id,'name':'AR'+str(entity_id-(nes+1)),'shape':'Triangle','tables':[],'relationships':[]}
            #Use the "argument" array from ClusterTables to list the lines that should connect AEs to ARs
            for inter in range(len(argument[i-(nes+1)])):
                if argument[i-(nes+1)][inter]:
                    abstract_schema['relationships'].append({'from':entity_id,'to':inter})
        #If it's an entity...
        else:
            #Just add it to the entities list
            entity = {'entity_id':entity_id,'name':'AE'+str(entity_id),'tables':[],'relationships':[]}
        entity_id+=1
        #Populate the entity with the proper tables, converting them to "front end" format
        for tab in cluster[i]['t']:
            table = [t for t in tables if t['name']==tab]
            table = table[0]
            entity['tables'].append({
                'table_id':table_id,
                'name':table['name'],
                'primary_keys':table['pks'],
                'attributes':[a for a in table['attributes'] if a not in table['pks']]})
            table_id+=1
        entities.append(entity)
    abstract_schema['entities'] = entities
    #Link all the tables within each entities by their primary keys
    for rel in relationships:
        curr_from = 0
        curr_to = 0
        for e in entities:
            for t in e['tables']:
                if t['name'] == rel['from']:
                    curr_from = t['table_id']
                if t['name'] == rel['to']:
                    curr_to = t['table_id']
            if curr_from and curr_to:
                e['relationships'].append({'from':curr_from,'to':curr_to})
    return(abstract_schema)
        

def tabKey(table):
    """Used for custom sorting by number of primary keys and lexigraphic order"""
    return ''.join([str(len(table['pks']))]+table['pks']);

def ClusterTables(tables):
    """Generates an abstract schema based on the database information using the algorithm outlined in class"""
    clusters = []
    remTabs = copy.deepcopy(tables)
    #insert the first table into an AE
    #remTabs is the tables left to handle
    #The rest of this algorithm is explained fully in the provided article
    clusters.append({'t':[tables[0]['name']],'pks':[key for key in tables[0]['pks']]})
    remTabs.remove(tables[0])
    nes = 0
    for i in range(1,len(tables)):
        R = tables[i]
        if R['pks'] == clusters[nes]['pks']:
            clusters[nes]['t'].append(R['name'])
            remTabs.remove(R)
        else:
            dj = True
            for j in range(0,nes+1):
                if not disjoint(R['pks'],clusters[j]['pks']):
                    dj = False
            if dj:
                nes+=1
                clusters.append({'t':[R['name']],'pks':[key for key in R['pks']]})
                remTabs.remove(R)

    for R in copy.deepcopy(remTabs):
        i = 0
        for i in range(nes+1):
            if not disjoint(R['pks'],clusters[i]['pks']):
                dj = True
                for j in range(nes+1):
                    if j!=i and not disjoint(R['pks'],clusters[j]['pks']):
                        dj = False
                if dj:
                    clusters[i]['t'].append(R['name'])
                    for pk in R['pks']:
                        if pk not in clusters[i]['pks']:
                            clusters[i]['pks'].append(pk)
                    remTabs.remove(R);
                    break

    intersects = [0 for i in range(nes+1)]
    argument = [[0 for i in range(nes+1)] for j in range(nes**2)]

    nas = nes+1
    first_rel = True
    for R in copy.deepcopy(remTabs):
        for i in range(nes+1):
            if not disjoint(R['pks'],clusters[i]['pks']):
                intersects[i] = 1
            else:
                intersects[i] = 0
        if first_rel:
            argument[0] = [n for n in intersects]
            clusters.append({'t':[R['name']],'pks':[key for key in R['pks']]})
            remTabs.remove(R)
            first_rel = False
        else:
            found = False
            for j in range(nes+1):
                if argument[j] == intersects:
                    target = j+nes+1
                    clusters[target]['t'].append(R['name'])
                    for pk in R['pks']:
                        if pk not in clusters[target]['pks']:
                            clusters[target]['pks'].append(pk)
                    remTabs.remove(R);
                    found = True
                    break;
            if not found:
                argument[nas-nes] = [n for n in intersects]
                nas+=1
                clusters.append({'t':[R['name']],'pks':[key for key in R['pks']]})
                remTabs.remove(R)
    return {'cluster':clusters,'nes':nes,'nas':nas,'arg':argument}

def disjoint(l1,l2):
    """Returns true if the given lists share no elements, else false."""
    return len([x for x in l1 if x in l2])==0
