import json
import networkx as nx
import ocel as ocel_lib
import pickle
import os
import shutil
import copy
import numpy as np

import pandas as pd
# import matplotlib.pyplot as plt
from pycelonis import get_celonis
from pandas import json_normalize


# convert celonis activity table dataframe to pandas dataframe based on ocel events
def convertCelonisActDfToEventDf(tableDf, caseColumn, activityColumn, timestampColumn):
    newTable = copy.deepcopy(tableDf)
    columns = [("ocel:omap", "ocel:omap"), ("ocel:activity", "ocel:activity"), ("ocel:timestamp", "ocel:timestamp")]
    remainingColumns = newTable.drop([caseColumn, activityColumn, timestampColumn], axis="columns").columns
        
    # in case we don't have any attributes in vmap, add empty vmap
    for col in remainingColumns:
        columns.append(("ocel:vmap", col))
    
    newTable[caseColumn] = newTable[caseColumn].apply(lambda x : [x])
    newTable.columns = pd.MultiIndex.from_tuples(columns)
    return newTable


# convert celonis object table dataframe to pandas dataframe based on ocel objects
def convertCelonisCaseDfToObjectDf(tableDf, caseColumn):
    newTable = copy.deepcopy(tableDf)

    objType = caseColumn.replace(" ", "_")
    newTable.index = newTable[caseColumn]
    newTable.index.rename(objType, inplace = True)
    newTable.drop(caseColumn, axis="columns", inplace=True)
    
    columns = []
    
    for attr in newTable.columns:
        columns.append(("ocel:ovmap", "attr"))
    
    columns.append(("ocel:type", "ocel:type"))
    newTable["ocel:type"] = objType
    newTable.columns = pd.MultiIndex.from_tuples(columns)
    
    return newTable




# saves all tables in OCEL_Models directory: 
#    format: OCEL_Models is root folder, contains folder for data_model. 
#            data_model folder contains a folder for each activity table in Celonis with an event and object table
class OCEL_Model:
    def __init__(self, newFolderName, ocels=set(), obj_relation=set()):
        self.rootFolder = "OCEL_Models"
        newPath = os.path.join(self.rootFolder, newFolderName)
        
        # if directory for new ocel_model already exists, delete old directory, create new one
        if os.path.exists(newPath):
            shutil.rmtree(newPath)
        os.mkdir(newPath)
        
        self.folder = newPath # save dataframes as pql here
        self.ocels = ocels # format: set(name1, name2, ...)
        self.obj_relation = obj_relation
    
    def addEventObjectDf(self, name, eventsDf, objectsDf):
        newPath = os.path.join(self.folder, name)
        
        # remove if exists already
        if os.path.exists(newPath):
            shutil.rmtree(newPath)
        os.mkdir(newPath)
        
        eventsDf.to_pickle(os.path.join(newPath, "eventsDf.pkl"))
        objectsDf.to_pickle(os.path.join(newPath, "objectsDf.pkl"))            
        self.ocels.add(name)

    def setEventsDf(self, name, eventsDf):
        newPath = os.path.join(self.folder, name)
        
        # remove if exists already
        if not os.path.exists(newPath):
            os.mkdir(newPath)
        
        eventsDf.to_pickle(os.path.join(newPath, "eventsDf.pkl"))

        self.ocels.add(name)

    def setObjectsDf(self, name, objectsDf):
        newPath = os.path.join(self.folder, name)
        
        # remove if exists already
        if not os.path.exists(newPath):
            os.mkdir(newPath)
        
        objectsDf.to_pickle(os.path.join(newPath, "objectsDf.pkl"))

        self.ocels.add(name)
        
        
    def alignEventsObjects(self, name):
        # remove objects that aren't mentioned in any events
        # remove objects from events that aren't mentioned in objectsDf
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)
        objects = set(objectsDf.index)
        
        # remove objects from events (and delete events without objects)
        toBeRemoved = []
        for index, row in eventsDf.iterrows():
            relatedObjects = objects.intersection(row["ocel:omap"]["ocel:omap"])
            if len(relatedObjects) == 0:
                toBeRemoved.append(index)
            else:
                eventsDf.at[index, ("ocel:omap", "ocel:omap")] = list(relatedObjects)
        
        # drop rows
        eventsDf.drop(toBeRemoved, inplace=True)
        # reset index of events dataframe
        eventsDf.reset_index(inplace=True, drop=True)
        
        # remove objects not mentioned in any events
        mentionedObjects = set()
        for obj in eventsDf["ocel:omap"]["ocel:omap"]:
            mentionedObjects = mentionedObjects.union(obj)
        toRemovedObjects = objects.difference(mentionedObjects)
        objectsDf.drop(index=toRemovedObjects, inplace=True)
        
        self.setEventsDf(name, eventsDf)
        self.setObjectsDf(name, objectsDf)
        
        
    def removeOCEL(self, name):
        if name not in self.ocels:
            return True
        filePath = os.path.join(self.folder, name)
        if os.path.exists(filePath):
            os.remove(filePath)
            self.ocels.remove(name)
            return True
        return False
    
    def getEventsDf(self, name):
        if name not in self.ocels:
            return False
        filePath = os.path.join(self.folder, name)
        filePath = os.path.join(filePath, "eventsDf.pkl")

        return pd.read_pickle(filePath)
            
    def getObjectsDf(self, name):
        if name not in self.ocels:
            return False
        filePath = os.path.join(self.folder, name)
        filePath = os.path.join(filePath, "objectsDf.pkl")

        return pd.read_pickle(filePath)

    def getObjectTypes(self, name):
        return set(self.getObjectsDf(name)["ocel:type"]["ocel:type"])
    
    def getObjects(self, name):
        return set(self.getObjectsDf(name).index)
    
    def getActivities(self, name):
        return set(self.getEventsDf(name)["ocel:activity"]["ocel:activity"])
    
    def getEventAttributes(self, name):
        eventsDf = self.getEventsDf(name)
        if "ocel:vmap" in [tup[0] for tup in eventsDf.columns]:
            return [attr for attr in eventsDf["ocel:vmap"].columns]
        return set()
    
    def getObjectAttributes(self, name):
        objectsDf = self.getObjectsDf(name)
        if "ocel:ovmap" in [tup[0] for tup in objectsDf.columns]:
            return [attr for attr in objectsDf["ocel:ovmap"].columns]
        return set()
        
    def setRelation(self, relation):
        self.obj_relation = relation
    
    def getRelation(self):
        return self.obj_relation
    
    def getOcelNames(self):
        return self.ocels
    
    # transform ocel json based dictionary to pandas dataframe
    def transformDictToDf(self, dictionary):
        transformed = {}
        for ev_id, event in dictionary.items():
            innerTransformed = {}
            for key, value in event.items():
                if type(value) == dict: # key == "ocel:vmap" or key == "ocel:vmap":
                    for innerKey, innerValue in value.items():
                        innerTransformed[(key, innerKey)] = innerValue
                else:
                    innerTransformed[(key, key)] = value
            transformed[ev_id] = innerTransformed

        return pd.DataFrame.from_dict(transformed, orient="index")
    
    # transform pandas dataframe to dictionary that conforms to json ocel standard
    def transformDftoDict(self, dataframe):
        transformed = {}
        for i in dataframe.index:
            outerdict = {}
            row = dataframe.loc[i]
            for multiColumn in dataframe.columns:
                if multiColumn[0] == "ocel:vmap" or multiColumn[0] == "ocel:ovmap":
                    innerdict = {}
                    for attrKey in row[multiColumn[0]].keys():
                        innerdict[attrKey] = row[multiColumn[0]][attrKey]
                    outerdict[multiColumn[0]] = innerdict
                else:
                    outerdict[multiColumn[0]] = row[multiColumn[0]][multiColumn[1]]
            transformed[i] = outerdict
        return transformed
    
    
    def transformEventDfObjectDfToOcel(self, name):
        eventDf = self.getEventsDf(name)
        objectDf = self.getObjectsDf(name)
        allActivities = list(set(eventDf["ocel:activity"]["ocel:activity"]))
        allObjects = list(set(objectDf.index))
        objectTypes = list(set(objectDf["ocel:type"]["ocel:type"]))
        attributeNames = []
        if "ocel:vmap" in eventDf.columns:
            attributeNames = list(set(eventDf["ocel:vmap"].columns))
        if "ocel:ovmap" in objectDf.columns:
            attributeNames = list(set(attributeNames).union(set(objectDf["ocel:ovmap"].columns)))
        eventDict = self.transformDftoDict(eventDf)
        # add empty vmap inc ase it doesnt exist
        for ev_id in eventDict:
            if "ocel:vmap" not in eventDict[ev_id]:
                eventDict[ev_id]["ocel:vmap"] = {}
        objectDict = self.transformDftoDict(objectDf)
        # add empty ovmap in case it doesnt exist
        for obj in objectDict:
            if "ocel:ovmap" not in objectDict[obj]:
                objectDict[obj]["ocel:ovmap"] = {}

        ocel = {}

        # set globals
        ocel["ocel:global-event"] = {"ocel:activity" : allActivities}
        ocel["ocel:global-object"] = {"ocel:type" : allObjects}
        ocel["ocel:global-log"] = {"ocel:attribute-names" : attributeNames}
        ocel["ocel:object-types"] = objectTypes

        # set events
        ocel["ocel:events"] = eventDict
        #set objects
        ocel["ocel:objects"] = objectDict

        # save to file and validate with schema

        return ocel
    
    def transformOcelToEventDfObjectDf(self, ocelFile="", ocel = False):
        if not ocel:
            with open(ocelFile) as json_file:
                ocel = json.load(json_file)
        else:
            ocel = ocel
        eventDf = self.transformDictToDf(ocel["ocel:events"])
        objectDf = self.transformDictToDf(ocel["ocel:objects"])
        
        name = ocelFile
        self.addEventObjectDf(name, eventDf, objectDf)
        return (eventDf, objectDf)

    
    ############################   OPERATORS:   ############################

    # input: 2 ocels, object relationship, attribute name(s) from ocels
    # output: 1 ocel, objects from log2 merged into log1 based on matches in event values of passed attribute(s)
    # attribute 1 are attribute names from log1, while attribute2 are attribute names from log2
    def matchMiner(self, name1, name2, attribute1, attribute2="", newName = ""):

        try:
            # if only one attribute passed, use it for both logs
            if attribute2 == "":
                attribute2 = attribute1

            # get logs
            eventsDf1 = self.getEventsDf(name1)
            objectsDf1 = self.getObjectsDf(name1)
            eventsDf2 = self.getEventsDf(name2)
            objectsDf2 = self.getObjectsDf(name2)

            # start from log1 since we want to merge objects from log2 into log1
            newEventsDf = copy.deepcopy(eventsDf1)
            newObjectsDf = copy.deepcopy(objectsDf1)
            
            object_relation = self.getRelation()

            # keep track of all added objects
            addedObjects = set()

            # iterate through events in first log and add objects from events in log2 with same vmap values for passed attributes (if in object relation)
            attributes = eventsDf1.to_dict()[("ocel:vmap", attribute1)]
            for ev_id, value in attributes.items():
                objects1 = eventsDf1.loc[ev_id][("ocel:omap", "ocel:omap")]

                newObjects = set()
                for objects2 in eventsDf2[eventsDf2[("ocel:vmap", attribute2)] == value][("ocel:omap", "ocel:omap")]:
                    
                    # only add those objects that are in the object relation
                    relatedObjects = set()
                    for obj1 in objects1:
                        for obj2 in objects2:
                            if (obj1, obj2) in object_relation:
                                relatedObjects.add(obj2)
                        
                    newObjects = newObjects.union(relatedObjects)

                newEventsDf.at[ev_id, ("ocel:omap", "ocel:omap")] = list(newObjects.union(eventsDf1[("ocel:omap", "ocel:omap")].loc[ev_id]))

                addedObjects = addedObjects.union(newObjects)

            # add new objects from log2 to log1
            toBeAddedObjects = list(addedObjects.difference(objectsDf1.index))
            newObjectsDf = pd.concat([objectsDf1, objectsDf2.loc[toBeAddedObjects]])

            # if no new name given, create own
            if newName == "":
                newName = "MATCH_MINER(" + name1 + "," + name2 + ")"

            self.addEventObjectDf(newName, newEventsDf, newObjectsDf)

            return True

        except:
            return False

        
    # input: 2 ocels, object relationship, activity relationship
    # output: 1 ocel, objects from log2 merged into log1 based on object and activity relation
    def manualMiner(self, name1, name2, activity_relation, newName=""):

        # get logs
        eventsDf1 = self.getEventsDf(name1)
        objectsDf1 = self.getObjectsDf(name1)
        eventsDf2 = self.getEventsDf(name2)
        objectsDf2 = self.getObjectsDf(name2)

        # start from log1 since we want to merge objects from log2 into log1
        newEventsDf = copy.deepcopy(eventsDf1)
        newObjectsDf = copy.deepcopy(objectsDf1)

        object_relation = self.getRelation()

        # keep track of all added objects
        addedObjects = set()

        for ev_id1 in eventsDf1.index:
            event1 = eventsDf1.loc[ev_id1]
            activity1 = event1[("ocel:activity", "ocel:activity")]
            objects1 = event1[("ocel:omap", "ocel:omap")]

            newObjects = set()

            for ev_id2 in eventsDf2.index:
                event2 = eventsDf2.loc[ev_id2]
                activity2 = event2[("ocel:activity", "ocel:activity")]
                objects2 = event2[("ocel:omap", "ocel:omap")]

                if (activity1, activity2) in activity_relation:

                    # only add those objects that are in the object relation
                    relatedObjects = set()
                    for obj1 in objects1:
                        for obj2 in objects2:
                            if (obj1, obj2) in object_relation:
                                relatedObjects.add(obj2)

                    newObjects = newObjects.union(relatedObjects)

            # add new objects to new datafrage
            newEventsDf.at[ev_id1, ("ocel:omap", "ocel:omap")] = list(newObjects.union(eventsDf1[("ocel:omap", "ocel:omap")].loc[ev_id1]))

            addedObjects = addedObjects.union(newObjects)

        # add new objects from log2 to log1
        toBeAddedObjects = list(addedObjects.difference(objectsDf1.index))
        newObjectsDf = pd.concat([objectsDf1, objectsDf2.loc[toBeAddedObjects]])

        # if no new name given, create own
        if newName == "":
            newName = "MANUAL_MINER(" + name1 + "," + name2 + ")"

        self.addEventObjectDf(newName, newEventsDf, newObjectsDf)    

        return True

    
    # concat operator, simply merges all events into one log, does not group any objects, sorts events on timestamp
    def concat(self, name1, name2, newName=""):

        # get logs
        eventsDf1 = self.getEventsDf(name1)
        objectsDf1 = self.getObjectsDf(name1)
        eventsDf2 = self.getEventsDf(name2)
        objectsDf2 = self.getObjectsDf(name2)

        # concatonate dataframes
        newEventsDf = pd.concat([eventsDf1, eventsDf2])
        newObjectsDf = pd.concat([objectsDf1, objectsDf2])
        
        # sort based on timestamps and reset index
        newEventsDf = newEventsDf.sort_values(by=[("ocel:timestamp", "ocel:timestamp")]).reset_index(drop=True)

        # if no new name given, create own
        if newName == "":
            newName = "CONCAT(" + name1 + "," + name2 + ")"

        self.addEventObjectDf(newName, newEventsDf, newObjectsDf)    

        return True

    
    # aggregate operator (merge objects of events with same activty / timestamp into first occurence)
    def aggregate(self, name, newName=""):

        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)

        newEventsDf = copy.deepcopy(eventsDf)

        # find duplicate activity and timestamps
        duplicateRowsDF = eventsDf[eventsDf.duplicated(subset=[("ocel:activity", "ocel:activity"), ("ocel:timestamp","ocel:timestamp")], keep=False)]
        activity = ""
        timestamp = ""
        objects = {}
        startIndex = 0
        for index, row in duplicateRowsDF.iterrows():
            act = row[("ocel:activity", "ocel:activity")]
            time = row[("ocel:timestamp", "ocel:timestamp")]
            obj = row[("ocel:omap", "ocel:omap")]
            if act == activity and time == timestamp:
                objects[startIndex] += obj
            else:
                startIndex = index
                activity = act
                timestamp = time
                objects[startIndex] = obj

        # aggregate objects of duplicate rows
        for index, obj in objects.items():
            newEventsDf.at[index, ("ocel:omap", "ocel:omap")] = list(set(obj))

        # remove duplicate rows
        toBeRemovedRows = eventsDf[eventsDf.duplicated(subset=[("ocel:activity", "ocel:activity"), ("ocel:timestamp","ocel:timestamp")], keep="first")].index
        newEventsDf.drop(toBeRemovedRows, inplace=True)
        
        # reset index of events dataframe
        eventsDf.reset_index(inplace=True, drop=True)
        
        # if no new name given, create own
        if newName == "":
            newName = "AGGREGATE(" + name + ")"

        self.addEventObjectDf(newName, newEventsDf, objectsDf)   
        
        return True
    
    
    # flattening operator that transforms all events to one object notion
    def flatten(self, name, objectType, newName=""):

        # get logs
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)    

        newEventsDf = copy.deepcopy(eventsDf)
        newObjectsDf = copy.deepcopy(objectsDf)

        object_relation = self.getRelation()

        # find all objects of type objectType
        allObjects = set(objectsDf[objectsDf[("ocel:type", "ocel:type")] == objectType].index)


        for ev_id, event in eventsDf.iterrows():
            relatedObjects = event[("ocel:omap", "ocel:omap")]
            toBeAddedObjects = allObjects.intersection(relatedObjects) # related objects that already are of correct type
            relatedObjects = set(relatedObjects).difference(toBeAddedObjects) # remaining objects

            # check which objects from relatedObjects are in relation with objects from objectType
            for relatedObj in relatedObjects:
                for obj in allObjects:
                    if (relatedObj, obj) in object_relation:
                        toBeAddedObjects.add(obj)

            # remove event if no related objects of correct type
            if len(toBeAddedObjects) == 0:
                newEventsDf.drop(ev_id, inplace=True)
            else:
                # set omap of event to only objects from type objectType
                newEventsDf.at[ev_id, ("ocel:omap", "ocel:omap")] = list(toBeAddedObjects)

        # remove objects of other type from objectsDf
        newObjectsDf.drop(newObjectsDf[newObjectsDf[("ocel:type", "ocel:type")] != objectType].index, inplace=True)

        # reset index of events dataframe
        eventsDf.reset_index(inplace=True, drop=True)

        # if no new name given, create own
        if newName == "":
            newName = "FLATTEN(" + name + ")"

        self.addEventObjectDf(newName, newEventsDf, newObjectsDf)    

        return True    
    

    # filter operator section start ----------------------------------------------------------------------


    # activities: set of activities
    # filter out events that aren't in activities parameter set
    def filterByActivity(self, eventsDf, activities):
        return eventsDf[eventsDf[("ocel:activity", "ocel:activity")].isin(activities)]


    # attributes parameter: dictionary with attribute name and set of acceptable values
    # events have to match all passed attributes
    def filterByAttribute(self, eventsDf, attributes):
        toBeRemoved = []
        for index, event in eventsDf.iterrows():
            for key, values in attributes.items():
                if ("ocel:vmap", key) not in eventsDf.columns:
                    toBeRemoved.append(index)
                    break
                elif event[("ocel:vmap", key)] not in values:
                    toBeRemoved.append(index)
                    break

        eventsDf.drop(toBeRemoved, inplace=True)

        return eventsDf


    # objects parameters: set of objects that we want to keep
    def filterByObject(self, eventsDf, objects):

        objects = set(objects)

        toBeRemoved = []
        for index, event in eventsDf.iterrows():
            intersec = objects.intersection(event[("ocel:omap", "ocel:omap")])
            if intersec == set():
                toBeRemoved.append(index)
            else:
                eventsDf.at[index, ("ocel:omap", "ocel:omap")] = list(intersec)

        eventsDf.drop(toBeRemoved, inplace=True)

        return eventsDf


    # timestamps parameter: (start_datetime, end_datetime)
    def filterByTimestamp(self, eventsDf, timestamps):

        start_datetime = timestamps[0]
        end_datetime = timestamps[1]

        return eventsDf[ (eventsDf[("ocel:timestamp", "ocel:timestamp")] <= end_datetime) & (eventsDf[("ocel:timestamp", "ocel:timestamp")] >= start_datetime)]



    # filter modes:
    #    activity, attribute, object, timestamp
    # parameters:
    #    actual filter criteria
    def filterLog(self, name, parameters, mode="activity", newName=""):

        # get logs
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)    

        newEventsDf = copy.deepcopy(eventsDf)

        if mode == "activity":
            newEventsDf = self.filterByActivity(newEventsDf, parameters)
        elif mode == "attribute":
            newEventsDf = self.filterByAttribute(newEventsDf, parameters)
        elif mode == "object":
            newEventsDf = self.filterByObject(newEventsDf, parameters)
        elif mode == "timestamp":
            newEventsDf = self.filterByTimestamp(newEventsDf, parameters)

        # reset index of events dataframe
        newEventsDf.reset_index(inplace=True, drop=True)

        # if no new name given, create own
        if newName == "":
            newName = "FILTER(" + name + ")"

        self.addEventObjectDf(newName, newEventsDf, objectsDf)

        # align objects and events (remove unmentioned objects after filtering)
        self.alignEventsObjects(newName)

        return True
    

    # interleaved miner section start ----------------------------------------------------------------------
    def sortByTimeStamp(self, element):
        return element[2][("ocel:timestamp", "ocel:timestamp")]


    # calculates interleaved event relation of two logs, used as helper for interleaved miner
    def interleavedRelation(self, eventsDf1, eventsDf2, obj1, obj2):
        # calculate path from obj1 and obj2
        path = []
        for ev_id, event in eventsDf1.iterrows():
            if obj1 in event[("ocel:omap", "ocel:omap")]:
                path.append((1, ev_id, event))

        for ev_id, event in eventsDf2.iterrows():
            if obj2 in event[("ocel:omap", "ocel:omap")]:
                path.append((2, ev_id, event))

        path.sort(reverse=False, key=self.sortByTimeStamp)

        matchingEvents = set()

        for i in range(len(path)-1):
            if path[i][0] != path[i+1][0]:
                matchingEvents.add((path[i][:2], path[i+1][:2]))

        # returns set of relation tuples. Each tuple contains two tuples, 
        # first element of inner tuple indicates which log, second element indicates event id
        return matchingEvents


    # calculates non interleaved event relation of two logs, used as helper for non/interleaved miner
    def nonInterleavedRelation(self, eventsDf1, eventsDf2, obj1, obj2):
        # calculate path from obj1 and obj2
        path = []
        for ev_id, event in eventsDf1.iterrows():
            if obj1 in event[("ocel:omap", "ocel:omap")]:
                path.append((1, ev_id, event))

        for ev_id, event in eventsDf2.iterrows():
            if obj2 in event[("ocel:omap", "ocel:omap")]:
                path.append((2, ev_id, event))

        path.sort(reverse=False, key=self.sortByTimeStamp)

        matchingEvents = set()

        for i in range(len(path)-1):
            if path[i][0] != path[i+1][0]:
                if i+2 == len(path) or path[i+1][0] == path[i+2][0]:
                    matchingEvents.add((path[i][:2], path[i+1][:2]))

        # returns set of relation tuples. Each tuple contains two tuples, 
        # first element of inner tuple indicates which log, second element indicates event id
        return matchingEvents


    # interleaved and non-interleaved miner, depending on interleavedMode flag value
    def interleavedMiner(self, name1, name2, interleavedMode=True, newName=""):
        # get logs
        eventsDf1 = self.getEventsDf(name1)
        objectsDf1 = self.getObjectsDf(name1)
        eventsDf2 = self.getEventsDf(name2)
        objectsDf2 = self.getObjectsDf(name2)

        # start from log1 since we want to merge objects from log2 into log1
        newEventsDf = copy.deepcopy(eventsDf1)
        newObjectsDf = copy.deepcopy(objectsDf1)

        object_relation = self.getRelation()

        newObjEventPairs = set()

        log1_objects = objectsDf1.index
        log2_objects = objectsDf2.index


        # restrict object relationship to objects in the logs
        crt_prd = [(x,y) for x in log1_objects for y in log2_objects]
        reduced_object_relation = set(crt_prd).intersection(object_relation)

        interleavedDict = {}
        for relation in reduced_object_relation:
            if interleavedMode:
                interleavedDict[relation] = self.interleavedRelation(eventsDf1, eventsDf2, relation[0], relation[1])
            else:
                interleavedDict[relation] = self.nonInterleavedRelation(eventsDf1, eventsDf2, relation[0], relation[1])


        for ev_id1, event1 in eventsDf1.iterrows():
            for obj1 in log1_objects:
                for relation in reduced_object_relation:
                    if relation[0] == obj1:
                        obj2 = relation[1]
                        for ev_id2, event2 in eventsDf2.iterrows():
                            if obj2 in log2_objects:
                                if ((1, ev_id1), (2, ev_id2)) in interleavedDict[(obj1, obj2)]:
                                    newObjEventPairs.add((ev_id1, obj2, ev_id2))

        # add new pairs to newLog
        for pair in newObjEventPairs:
            ev_id = pair[0]
            obj = pair[1]
            ev_id2 = pair[2]

            # add new object to event omap, but avoid duplicates
            objects = newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]
            objects.append(obj)
            newEventsDf.at[ev_id, ("ocel:omap", "ocel:omap")] = list(set(objects))

            # fix vmap
            for key, value in eventsDf2.loc[ev_id2]["ocel:vmap"].items():
                if key not in newEventsDf.loc[ev_id]['ocel:vmap'].keys():
                    newEventsDf[("ocel:vmap", key)] = np.nan
                    newEventsDf.at[ev_id, ('ocel:vmap', key)] = value


            # add new object to objects of log
            mentionedObjects = set()
            for obj in newEventsDf[("ocel:omap", "ocel:omap")]:
                mentionedObjects = mentionedObjects.union(obj)
            toBeAddedObjects = list(mentionedObjects.difference(newObjectsDf.index))
            newObjectsDf = pd.concat([newObjectsDf, objectsDf2.loc[toBeAddedObjects]])

        # if no new name given, create own
        if newName == "":
            newName = "NON/INTERLEAVED(" + name1 + "," + name2 + ")"

        self.addEventObjectDf(newName, newEventsDf, newObjectsDf)

        return True