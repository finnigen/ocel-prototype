import json
import networkx as nx
import ocel as ocel_lib
import pickle

import pandas as pd
# import matplotlib.pyplot as plt
from pycelonis import get_celonis


class OCEL_Model:
    def __init__(self, ocels={}, obj_relation=set()):
        self.ocels = ocels # format: {name1: ocel1, name2: ocel2 ... }
        self.obj_relation = obj_relation
    
    def addOCEL(self, name, ocel):
        self.ocels[name] = ocel

    def removeOCEL(self, name):
        del self.ocels[name]




def convertToOcelModel(url, api_token, data_pool, data_model):
    # establish connection
    # download data
    # create ocels
    # create object relationships
    # convert to OCEL_Model class

    print("Establishing connection to Celonis...")

    celonis = get_celonis(url, api_token)

    data_pool = celonis.pools.find(data_pool)
    data_model = data_pool.datamodels.find(data_model)

    tables = {}
    all_data = {}

    print("Downloading data...")
    for conf in data_model.process_configurations:
        table_name = conf.activity_table.name
        tables[table_name] = conf
        all_data[table_name] = tables[table_name].activity_table.get_data_frame()
        all_data[tables[table_name].case_table.name] = tables[table_name].case_table.get_data_frame()

    ocels = {}
    for table in tables:
        
        print("Transforming " + str(table) + " table...")
        
        attribute_names = set()
        object_types = set()
        activities = set()
        global_objects = set()
        
        print("Fetching Data...")
        df = all_data[table]
        case_table = all_data[tables[table].case_table.name]
        case_table_case_column = tables[table].case_column # ASSUME SAME AS IN ACTIVITY TABLE
        
        
        act_column = tables[table].activity_column
        time_column = tables[table].timestamp_column
        case_column = tables[table].case_column
        attr_columns = df.columns.difference([act_column, time_column, case_column, tables[table].sorting_column])
        
        attribute_names = attribute_names.union(attr_columns)
        
        print("   Transforming Events...")
        events = {}
        for row in df.iterrows():
            event = row[1]

            o = {"ocel:activity": event}
            o["ocel:activity"] = event[act_column]
            
            activities.add(event[act_column])
            
            o["ocel:timestamp"] = str(event[time_column])
            o["ocel:omap"] = [ event[case_column] ]
            o["ocel:vmap"] = {col: event[col] for col in attr_columns}


            events[str(row[0])] = o
        
        
        print("   Transforming Objects...")

        attr_columns = case_table.columns.difference([case_table_case_column])
        
        attribute_names = attribute_names.union(attr_columns)
        
        objects = {}
        for row in case_table.iterrows():
            event = row[1]

            o = {}
            o["ocel:type"] = case_table_case_column
            o["ocel:ovmap"] = {col: event[col] for col in attr_columns}

            objects[str(event[case_table_case_column])] = o 
            
            global_objects.add(str(event[case_table_case_column]))
            
        object_types.add(str(case_table_case_column))
            
        print("   Global Values...")
        ocel = {  "ocel:global-event": {"ocel:activity": list(activities)}}
        ocel["ocel:global-object"] =  {"ocel:type": "__INVALID__"} # {"ocel:type": list(global_objects)}
        ocel["ocel:global-log"] = {"ocel:attribute-names": list(attribute_names),
                                    "ocel:object-types": list(object_types),
                                    "ocel:version": "1.0",
                                    "ocel:ordering": "timestamp"}
        ocel["ocel:events"] = events
        ocel["ocel:objects"] = objects
        
        ocels[table] = ocel

    print("Validating OCELs...")
    for o in ocels:
        ocel_lib.export_log(ocels[o], 'oceltest.json')
        if not ocel_lib.validate('oceltest.json', 'schema.json'):
            print(ocels[o])
            raise Exception("INVALID OCEL DOES NOT MATCH SCHEMA")
    print("All logs validated successfully...")





    print("Generating object relationships...")


    object_relations = {}

    foreignKeys = data_model.foreign_keys
    all_tables = data_model.tables

    product = []
    for x in tables.keys():
        for y in tables.keys():
            if (y, x) not in product and x != y:
                product.append((x, y))

        
    print("Creating foreign key graph...")

    graph = {}
    for table in all_tables.names.keys():
        connected_nodes = [] 
        for dictionary in foreignKeys.find_keys_by_source_name(table):
            connected_nodes.append(dictionary["target_table"])
            for dictionary in foreignKeys.find_keys_by_target_name(table):
                connected_nodes.append(dictionary["source_table"])
            graph[table] = connected_nodes

    G = nx.Graph()
    for i in graph:
        G.add_node(i)
        for j in graph[i]:
            G.add_edge(i, j)

        foreignKeyGraph = G


    for pair in product:
        table1 = pair[0]
        table2 = pair[1]
        
        print("Object relations between: " + table1 + " and " + table2)
            
        path = nx.algorithms.shortest_paths.generic.shortest_path(foreignKeyGraph, source=table1, target=table2)


        print("   Calculating join path...")

        potential_relations2 = foreignKeys.find_keys_by_source_name(path[0]) + foreignKeys.find_keys_by_target_name(path[0])
        mergePath = []
        for i in range(len(path)-1):
            potential_relations1 = potential_relations2
            potential_relations2 = foreignKeys.find_keys_by_source_name(path[i+1]) + foreignKeys.find_keys_by_target_name(path[i+1])
            key_relation = {}
            for relation in potential_relations1:
                if relation in potential_relations2:
                    key_relation = relation
                    break
            if key_relation == {}:
                print("No Relation Found!")
                break
            mergePath.append({"leftTable": key_relation["source_table"], "leftColumn": key_relation["columns"][0][0], 
                                "rightTable": key_relation["target_table"], "rightColumn": key_relation["columns"][0][1]})

        
        print("   Getting data...")
        
        for tab in path:
            if tab not in all_data:
                all_data[tab] = data_model.tables.find(tab).get_data_frame()
        
        print("   Joining tables...")

        df = all_data[table1]
        for relation in mergePath:
            df = df.merge(all_data[relation["leftTable"]] \
                .merge(all_data[relation["rightTable"]], \
                        left_on=relation["leftColumn"], right_on=relation["rightColumn"]))

        columns_to_keep = [tables[table1].case_column, tables[table2].case_column]

        df = df[list(set(columns_to_keep).intersection(df.columns))]

        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        object_relations[(table1, table2)] = df
        object_relations[(table2, table1)] = df


    total_relation = set()
    for i in range(len(tables)):
        for j in range(len(tables)):
            if i != j:
                df = object_relations[(list(tables.keys())[i], list(tables.keys())[j])]
                for tup in df.to_records():
                    total_relation.add((tup[1], tup[2]))
                    total_relation.add((tup[2], tup[1]))

    return OCEL_Model(ocels, total_relation)




url = "https://louis-herrmann-rwth-aachen-de.training.celonis.cloud"
api = "NWE2NjdjOGEtYTkyMS00NDYyLTk0M2EtZjFiYjdhZDA5MTYzOmZJSDIydFd3TEwrQkUwV2tBVkhtN0N5VFI1aHdWYVJ2TDJVUWpoL2U5cUE4"

data_pool = "OCEL_Pool1"
data_model = "OCEL_Model1"

# ocel_model = convertToOcelModel(url, api, data_pool, data_model)

# for development purposes
def saveToPickle():
    ocel_model = convertToOcelModel(url, api, data_pool, data_model)
    with open('file.pkl', 'wb') as file:
        pickle.dump(ocel_model, file)

# saveToPickle()