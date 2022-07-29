import json
import networkx as nx
import ocel as ocel_lib
import pickle

import pandas as pd
# import matplotlib.pyplot as plt
from pycelonis import get_celonis
from ocel_model import *


def convertToOcelModel(url, api_token, data_pool, data_model, skipConnection=False):
    # connect to Celonis
    # download all data
    # for all activity tables:
        # associate case and activity table 
        # convert Celonis ActDf To EventDf and convert Celonis CaseDf To ObjectDf and add to OCEL_Model
    # calculate object relationships
    # add relationships to OCEL_Model
    
    if skipConnection: # in this case, we already get passed a full Celonis data model
        data_model = data_model
    else: # in this case, we first have to setup connection
        print("Establishing connection to Celonis...")

        celonis = get_celonis(url, api_token, key_type="USER_KEY")
        data_pool = celonis.pools.find(data_pool)
        data_model = data_pool.datamodels.find(data_model)

        
    # create ocel_Model object
    ocel_model = OCEL_Model(newFolderName = data_pool.name + "__" + data_model.name)

        
    tables = {}
    all_data = {}
    case_table_case_column = {} # keep track of case table's case column

    print("Downloading data...")
    for conf in data_model.process_configurations:
        table_name = conf.activity_table.name
        tables[table_name] = conf
        all_data[table_name] = tables[table_name].activity_table.get_data_frame()
        
        # sort based on sorting column. If there is no sorting column, use timestamp column
        sorting_column = tables[table_name].sorting_column
        if not sorting_column:
            sorting_column = tables[table_name].timestamp_column
        all_data[table_name].sort_values(sorting_column, inplace=True)
        
        # reset index after sorting
        all_data[table_name].reset_index(inplace=True)
        del all_data[table_name]["index"]
        
        # save case table
        case_table_name = tables[table_name].case_table.name
        all_data[case_table_name] = tables[table_name].case_table.get_data_frame()

    
    for table_name in tables:
        print("Transforming " + str(table_name) + " table...")
        
        print("Fetching Data...")
        df = all_data[table_name]
        case_table_name = tables[table_name].case_table.name
        case_table = all_data[case_table_name]
        
        # find case table's case column name by looking at foreign key relation
        activity_table_f_keys = data_model.foreign_keys.find_keys_by_name(table_name)
        case_table_f_keys = data_model.foreign_keys.find_keys_by_name(case_table_name)
        for key in activity_table_f_keys:
            if key in case_table_f_keys:
                if tables[table_name].case_column == key["columns"][0][0]:
                    case_table_case_column[table_name] =  key["columns"][0][1]
                else:
                    case_table_case_column[table_name] = key["columns"][0][0]
        
        # save case, activity, timestamp column name of activity table
        case_column = tables[table_name].case_column
        act_column = tables[table_name].activity_column
        time_column = tables[table_name].timestamp_column
        sorting_column = tables[table_name].sorting_column
        if not sorting_column:
            sorting_column = ""
 
        print("Converting to OCEL-Based Dataframes")
        # convert tables to OCEL-based dataframes
        eventsDf = convertCelonisActDfToEventDf(df, case_column, act_column, time_column, sorting_column)
        objectsDf = convertCelonisCaseDfToObjectDf(case_table, case_table_case_column[table_name])
        
        # add OCEL-based events and object dataframes to ocel_model
        ocel_model.addEventObjectDf(table_name, eventsDf, objectsDf)
        # align objects and events dataframe so that there aren't objects in objectsDf not mentioned in any events and no objects in eventsDf not mentioned in objectsDf (conflicts are being handles by removing events/objects)
        ocel_model.alignEventsObjects(table_name)
        

    print("Generating object relationships...")
        
    # prefix column names of all columns to ensure uniqueness. We do this before joining tables to compute obj relationships
    for table_name in all_data:
        all_data[table_name].columns = [table_name + column for column in all_data[table_name].columns]    
    

#    object_relations = {}

    foreignKeys = data_model.foreign_keys
    all_tables = data_model.tables

    # compute possible connections between activity tables
    product = []
    for x in tables.keys():
        for y in tables.keys():
            if (y, x) not in product and x != y:
                product.append((x, y))

        
    print("Creating foreign key graph...")
    
    # create foreign key graph so we can find shortest path from one activity table to another
    G = nx.DiGraph()
    for table in all_tables.names.keys():
        G.add_node(table)

    edgeAttr = {}
    for dictionary in foreignKeys:
        i = dictionary["source_table"]
        j = dictionary["target_table"]
        G.add_edge(i, j)
        edgeAttr[(i, j)] = {"columns": dictionary["columns"][0]}
        
        # make symmetric since we can merge both ways
        G.add_edge(j, i)
        edgeAttr[(j, i)] = {"columns": (dictionary["columns"][0][1], dictionary["columns"][0][0])}
        
    nx.set_edge_attributes(G, edgeAttr)

    foreignKeyGraph = G

    for pair in product:
        ev_table1 = pair[0]
        ev_table2 = pair[1]

        table1 = tables[ev_table1].case_table.name
        table2 = tables[ev_table2].case_table.name
        
        print("Object relations between: " + table1 + " and " + table2)
        
        # calculate path of tables to be merged on (if such a path exists)
        try:
            path = nx.algorithms.shortest_paths.generic.shortest_path(foreignKeyGraph, source=table1, target=table2)
        except:
            print("Not connected")
            continue

        print("   Calculating join path...")
        
        # calculate merge path with table names and column names of these tables to join on (format: [{"leftTable" : lTable, "leftColumn: lColumn, rightTable": rtable, "rightColumn": rColumn}, ...])
        mergePath = []
        for i in range(len(path) - 1):
            leftTable = path[i]
            rightTable = path[i+1]
            columns = foreignKeyGraph[leftTable][rightTable]["columns"]
            
            mergePath.append({"leftTable": leftTable, "leftColumn": leftTable + columns[0], 
                                "rightTable": rightTable, "rightColumn": rightTable + columns[1]})

        print("   Getting data...")
        
        # get data of other tables (so far we only downloaded case and activity table data)
        for tab in path:
            if tab not in all_data:
                all_data[tab] = data_model.tables.find(tab).get_data_frame()
                # prefix column names with table names to ensure uniquness
                all_data[tab].columns = [tab + column for column in all_data[tab].columns]
                
        print("   Joining tables...")
        
        # find columns we need for merging so that we can drop others for better efficiency
        remainingColumns = set()
        for d in mergePath:
            remainingColumns.add(d["leftColumn"])
            remainingColumns.add(d["rightColumn"])

        # perform pandas merge along merge path
        df = all_data[table1]
        for relation in mergePath:
            df = df.merge(all_data[relation["leftTable"]] \
                .merge(all_data[relation["rightTable"]], \
                        left_on=relation["leftColumn"], right_on=relation["rightColumn"]))
            df.drop(list(set(df.columns).difference(remainingColumns)), axis=1, inplace=True)
            
        # we only want the two object columns, so we can drop rest
        columns_to_keep = [table1 + case_table_case_column[ev_table1], table2 + case_table_case_column[ev_table2]]
        df = df[list(set(columns_to_keep).intersection(df.columns))]
        
        # reset index
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        
#        object_relations[(table1, table2)] = df
#        object_relations[(table2, table1)] = df

        total_relation = set()
        for tup in df.to_records():
            total_relation.add((tup[1], tup[2]))
            total_relation.add((tup[2], tup[1]))
        
        ocel_model.addToRelation(total_relation)
    
    print("Making object relation reflexive...")    
    # make object relation reflexive
    reflexive = set()
    for tableName in ocel_model.getOcelNames():
        for obj in ocel_model.getObjects(tableName):
            reflexive.add((obj, obj))
    ocel_model.addToRelation(reflexive)


    # add all object relationships in form of tuples to a set
#    total_relation = set()
#    for i in range(len(tables)):
#        for j in range(len(tables)):
#            if i != j:
#                df = object_relations[(list(tables.keys())[i], list(tables.keys())[j])]
#                for tup in df.to_records():
#                    total_relation.add((tup[1], tup[2]))
#                    total_relation.add((tup[2], tup[1]))

#    ocel_model.setRelation(total_relation)
         
                    
    return ocel_model



#url = "https://louis-herrmann-rwth-aachen-de.training.celonis.cloud"
#api = "NWE2NjdjOGEtYTkyMS00NDYyLTk0M2EtZjFiYjdhZDA5MTYzOmZJSDIydFd3TEwrQkUwV2tBVkhtN0N5VFI1aHdWYVJ2TDJVUWpoL2U5cUE4"

#data_pool = "OCEL_Pool1"
#data_model = "OCEL_Model1"


url = "https://louis-herrmann-rwth-aachen-de.training.celonis.cloud"
api = "NWE2NjdjOGEtYTkyMS00NDYyLTk0M2EtZjFiYjdhZDA5MTYzOmZJSDIydFd3TEwrQkUwV2tBVkhtN0N5VFI1aHdWYVJ2TDJVUWpoL2U5cUE4"

url = "https://students-pads.eu-1.celonis.cloud"
api = "MmRlZTU4M2MtNjg5NS00YTU4LTlhOWEtODQ1ZDAxYTUzNTcxOmNaUjhMUllkSUQ4Y0E2cG9uRERkSWJSY2FtdVp0NkxLTVhuTm92TGk0Q0Fi"


data_pool = "OcelBigReduccedPool"
data_model = "OcelBigReducedModel"

data_pool = "DemoPool"
data_model = "DemoModel"

# data_pool = "BigTest"
# data_model = "BigModel1"

# data_pool = "SAPFixed"
# data_model = "SAPo2c"

# ocel_model = convertToOcelModel(url, api, data_pool, data_model)

# for development purposes
def saveToPickle(url, api, data_pool, data_model):
    ocel_model = convertToOcelModel(url, api, data_pool, data_model)
    with open('fileDf.pkl', 'wb') as file:
        pickle.dump(ocel_model, file)

# saveToPickle(url, api, data_pool, data_model)