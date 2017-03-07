import mysql.connector
import copy

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

def get_db_schema(d,u,p,h,o):
    print([u,d,p,h,o])
    try:
        cnx = mysql.connector.connect(user=u, database=d, password=p,host=h,port = o)
    except:
        print("Unable to connect to database")
        return None
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
        pris = []
        for col in colInfo:
            cols = cols + [col[0]]
            if col[3]=='PRI':
                pris.append(col[0])
        tables.append({"name":table[0],'attributes':cols,'pks':sorted(pris)})
    data['tables'] = tables
    #tables = TTables()
	
    for n in fkNames:
        relationships.append({'from':n[-2],'to':n[-1]})
    data['relationships'] = relationships
    clusters =  ClusterTables(sorted(tables,key=tabKey))
    data['cluster'] = get_abstract_schema(clusters,tables,relationships)

    cnx.close()
    return(data)

def TTables():
    tab = [
            {'name':'R1',
            'pks':['Ka','K1'],
            'attributes':[]},

            {'name':'R2',
            'pks':['Ka','K2'],
            'attributes':[]},

            {'name':'R3',
            'pks':['Ka','K3'],
            'attributes':[]},

            {'name':'R4',
            'pks':['Kc','Kx','K4'],
            'attributes':[]},

            {'name':'R5',
            'pks':['Kc','Kx','Kd','K5'],
            'attributes':[]},

            {'name':'R6',
            'pks':['Ka','Kb','K6'],
            'attributes':[]},

            {'name':'R7',
            'pks':['Ka','Kc','Kx','Ke','K7'],
            'attributes':[]},
            
            {'name':'R8',
            'pks':['Ka','Ka','K8'],
            'attributes':[]},

            {'name':'R9',
            'pks':['Ka','Kb','Kc','Kx','Kd','K9'],
            'attributes':[]},

            {'name':'R10',
            'pks':['Kc','Ky','K10'],
            'attributes':[]},

            {'name':'R11',
            'pks':['Ka','Kc','K11'],
            'attributes':[]}
            ]
    return tab

def get_abstract_schema(clusters,tables,relationships):
    cluster = clusters['cluster']
    nes = clusters['nes']
    nas = clusters['nas']
    abstract_schema = {'entities':[], 'relationships':[]}
    entities = []
    table_id = 0
    entity_id = 0
    for i in range(min(nas+1,len(cluster))):
        if i>nes:
            entity = {'entity_id':entity_id,'name':'AR'+str(entity_id-(nes+1)),'shape':'Triangle','tables':[],'relationships':[]}
            for pk in cluster[i]['pks']:
                for e in entities:
                    for t in e['tables']:
                        if pk in t['primary_keys']:
                            con_to = e['entity_id']
                            break
                abstract_schema['relationships'].append({'from':entity_id,'to':con_to})
        else:
            entity = {'entity_id':entity_id,'name':'AE'+str(entity_id),'tables':[],'relationships':[]}
        entity_id+=1
        for tab in cluster[i]['t']:
            table = [t for t in tables if t['name']==tab]
            table = table[0]
            entity['tables'].append({
                'table_id':table_id,
                'name':table['name'],
                'primary_keys':table['pks'],
                'attributes':table['attributes']})
            table_id+=1
        entities.append(entity)
    abstract_schema['entities'] = entities
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
    return ''.join([str(len(table['pks']))]+table['pks']);

def ClusterTables(tables):
    clusters = []
    remTabs = copy.deepcopy(tables)
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
    argument = []

    nas = nes+1
    first_rel = True
    for R in copy.deepcopy(remTabs):
        for i in range(nes+1):
            if not disjoint(R['pks'],clusters[i]['pks']):
                intersects[i] = 1
            else:
                intersects[i] = 0
        if first_rel:
            argument.append([n for n in intersects])
            clusters.append({'t':[R['name']],'pks':[key for key in R['pks']]})
            remTabs.remove(R)
            first_rel = False
        else:
            found = False
            for j in range(nas+1):
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
                nas+=1
                argument.append([n for n in intersects])
                clusters.append({'t':[R['name']],'pks':[key for key in R['pks']]})
                remTabs.remove(R)
    return {'cluster':clusters,'nes':nes,'nas':nas}

def OccOrderPKs(tabs):
    pks = {}
    for tab in tabs:
        for pk in tab['pks']:
            if pk not in pks:
                pks[pk] = 1
            else:
                pks[pk] += 1
    return sorted(pks,key=pks.get,reverse=True)


def disjoint(l1,l2):
   return len([x for x in l1 if x in l2])==0
