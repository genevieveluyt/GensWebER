import mysql.connector
import copy
import os
import javalang

DEBUG = False
VERBOSE = False

def get_db_schema(d,u,p,h,o,java_dir):
    """Get data for a high-level representation of a MySQL database schema.

    Keyword arguments:
    d -- MySQL database name
    u -- username that will be used to connect to the MySQL database
    p -- password that will be used to connect to the MySQL database
    h -- host that will be used to connect to the MySQL database
    o -- port that will be used to connect to the MySQL database
    dir -- directory in which to look for Java files that can be used to determine foreign key candidates
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

    fkCans = get_foreign_key_candidates(java_dir)

    for fk in fkCans:
        for ent in data['cluster']['entities']:
            f = None
            t = None
            for tName in ent['tables']:
                if tName["name"] == fk["table_name"]:
                    f = tName["table_id"]
                elif tName["name"] == fk["referenced_table_name"]:
                    t = tName["table_id"]
            if t is not None and f is not None:
                relExists = False
                for rel in ent["relationships"]:
                    if (rel["from"] == f and rel["to"] == t) or (rel["from"] == t and rel["to"] == f):
                        relExists = True
                        break
                if not relExists:
                    ent["relationships"].append({'from':f,'to':t,'isForeignKeyCandidate': True})
                break
    
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

    for i in range(max(nas,len(cluster))):
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
                relExists = False
                for e_rel in e["relationships"]:
                    if (e_rel["from"] == curr_from and e_rel["to"] == curr_to) or (e_rel["from"] == curr_to and e_rel["to"] == curr_from):
                        relExists = True
                        break
                if not relExists:
                    e['relationships'].append({'from':curr_from,'to':curr_to})
                break
                
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

def get_foreign_key_candidates(directory):
    """Get foreign key candidates by looking for @ManyToOne, @OneToOne, @OneToMany and @JoinColumn annotations in Java files.

    Keyword arguments:
    directory -- the local file directory containing Java files to parse for foreign key candidates
    """

    if not directory:
        return []

    # Maps absolute class names (package name + class name) to a database table specified with the @Table annotation
    class_table_map = dict()

    # Keeps track of class names in a package so that referenced class names not found in an import statement can be resolved
    package_classes = dict()

    foreign_key_candidates = []

    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename[-5:] == ".java":
                with open(os.path.join(root, filename), "r") as file:
                    java_tree = javalang.parse.parse(file.read())

                if java_tree.package is None:
                    package_name = ""
                else:
                    package_name = java_tree.package.name
                imports = [import_statement.path for import_statement in java_tree.imports]

                if DEBUG and VERBOSE:
                    print "File name: {}".format(filename)
                    print "Package: {}".format(package_name)
                    print "Imports: {}".format(imports)

                for path, class_node in java_tree.filter(javalang.tree.ClassDeclaration):
                    if package_name:
                        package_classes.setdefault(package_name, []).append(class_node.name)
                    class_name = "{}.{}".format(package_name, class_node.name)
                    table_name = None

                    # Look for @Table annotations and associate them with the class in class_table_map dictionary
                    for class_annotation in class_node.annotations:
                        if class_annotation.name == "Table":
                            for name_val in class_annotation.element or []:
                                if name_val.name == "name":
                                    table_name = name_val.value.value[1:-1]
                                    if DEBUG and class_name in class_table_map:
                                        print ("{} already mapped to a table...".format(class_name))
                                    class_table_map[class_name] = table_name            
                    
                    if not table_name:
                        continue

                    for field_node in class_node.fields:
                        relation_type = None
                        foreign_key_name = None
                        referenced_column_name = None
                        local_referenced_table_class = None

                        if type(field_node.type) is javalang.tree.BasicType:
                            continue
                        else:
                            if field_node.type.arguments:
                                # If the variable type is a generic class like Set<Admission> or List<org.Tickler>, get the class name from inside the angle brackets
                                var_type = field_node.type.arguments[0].type
                            else:
                                var_type = field_node.type
                            
                            if var_type.sub_type:
                                # If the variable type is an absolute class name like org.Admission.Tickler, walk through the nodes and turn it into a string
                                var_type_string = var_type.name
                                while var_type.sub_type:
                                    var_type = var_type.sub_type
                                    var_type_string += ".{}".format(var_type.name)
                                referenced_table_class = var_type_string
                            else:
                                # Else look for an import statement to get the absolute class name
                                var_class = var_type.name
                                var_import = next((item for item in imports if item[-len(var_class):] == var_class), None)
                                if var_import:
                                    referenced_table_class = var_import
                                elif var_class not in ['String', 'Integer', 'Double', 'Boolean']:
                                    # If there is no import statement for the class, the class is likely in another file in the same package. It will be determined after all files have been parsed.
                                    local_referenced_table_class = var_class
                                else:
                                    continue
                        
                        # Look for @ManyToOne, @OneToOne, @OneToMany and @JoinColumn annotations to get information about the foreign key and the primary key it references
                        for field_annotation in field_node.annotations:
                            if field_annotation.name in ["ManyToOne", "OneToOne", "OneToMany"]:
                                relation_type = field_annotation.name
                            if field_annotation.name == "JoinColumn":
                                for name_val in field_annotation.element or []:
                                    if name_val.name == "name":
                                        foreign_key_name = name_val.value.value[1:-1]
                                    elif name_val.name == "referencedColumnName":
                                        referenced_column_name = name_val.value.value[1:-1]
                                if not referenced_column_name:
                                    # If there is no referenced column specified, assume it is the same as the foreign key name
                                    referenced_column_name = foreign_key_name
                        if foreign_key_name:
                            foreign_key_candidates.append({
                                "relation_type": relation_type,
                                "foreign_key_name": foreign_key_name,
                                "table_name": table_name,
                                "class_name": class_name,
                                "referenced_key_name": referenced_column_name,
                                "referenced_table_class": referenced_table_class,
                                "referenced_table_name": None,  #placeholder
                                "package_name": package_name,
                                "local_referenced_table_class": local_referenced_table_class
                            })

    for foreign_key_candidate in foreign_key_candidates:
        local_referenced_table_class = foreign_key_candidate["local_referenced_table_class"]
        if local_referenced_table_class:
            # If a referenced class name could not be found in an import statement, look for it in the class's package
            package_name = foreign_key_candidate["package_name"]
            class_in_package = next((item for item in package_classes[package_name] if item[-len(local_referenced_table_class):] == local_referenced_table_class), None)
            if class_in_package:
                foreign_key_candidate["referenced_table_class"] = "{}.{}".format(package_name, local_referenced_table_class)
            elif DEBUG:
                print "Could not find absolute class name for {} in class {}".format(local_referenced_table_class, foreign_key_candidate["class_name"])

        referenced_table_name = class_table_map.get(foreign_key_candidate["referenced_table_class"], None)
        if referenced_table_name:
            foreign_key_candidate["referenced_table_name"] = referenced_table_name
        else:
            foreign_key_candidate["referenced_table_name"] = foreign_key_candidate["referenced_table_class"].split('.')[-1].lower()
            if DEBUG:
                print "Could not find table name for class {}. Using {}.".format(foreign_key_candidate["referenced_table_class"], foreign_key_candidate["referenced_table_name"]) 
                if VERBOSE:
                    print foreign_key_candidate
                    print ""

    if DEBUG:
        print [foreign_key for foreign_key in foreign_key_candidates if foreign_key["referenced_table_name"]]
    return [foreign_key for foreign_key in foreign_key_candidates if foreign_key["referenced_table_name"]]
