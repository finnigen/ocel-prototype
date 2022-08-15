import json
import networkx as nx
import ocel as ocel_lib
import pickle
import os
import shutil
import copy
import numpy as np
from datetime import timedelta

import pandas as pd
# import matplotlib.pyplot as plt
from pycelonis import get_celonis
from pandas import json_normalize
from datetime import timedelta
from itertools import product


class EmptyLogException(Exception):
    pass


# convert celonis activity table dataframe to pandas dataframe based on ocel events
def convertCelonisActDfToEventDf(tableDf, caseColumn, activityColumn, timestampColumn, sortingColumn=""): 
    newTable = copy.deepcopy(tableDf)
    
    # drop sorting columns
    if sortingColumn != "":
        newTable.drop(columns=[sortingColumn], inplace=True)

    newTable[caseColumn] = newTable[caseColumn].apply(lambda x : [x])

    columns={caseColumn:("ocel:omap", "ocel:omap"), activityColumn: ("ocel:activity", "ocel:activity"), timestampColumn: ("ocel:timestamp", "ocel:timestamp")}
    remainingColumns = newTable.drop([caseColumn, activityColumn, timestampColumn], axis="columns").columns
        
    # in case we don't have any attributes in vmap, add empty vmap
    for col in remainingColumns:
        columns[col] = ("ocel:vmap", col)
    
    newTable.rename(columns=columns, inplace=True)
    newTable.columns = pd.MultiIndex.from_tuples(newTable.columns)

    # reorder columns
    newTable = newTable[[("ocel:omap", "ocel:omap"), ("ocel:activity", "ocel:activity"), ("ocel:timestamp", "ocel:timestamp")] + list(newTable.drop(columns=[("ocel:omap", "ocel:omap"), ("ocel:activity", "ocel:activity"), ("ocel:timestamp", "ocel:timestamp")]).columns)]
    
    return newTable


# convert celonis object table dataframe to pandas dataframe based on ocel objects
def convertCelonisCaseDfToObjectDf(tableDf, caseColumn, table_name):
    newTable = copy.deepcopy(tableDf)

    objType = table_name.replace(" ", "_")
    newTable.index = newTable[caseColumn]
    newTable.index.rename(objType, inplace = True)
    newTable.drop(caseColumn, axis="columns", inplace=True)
    
    columns = {}
    
    for attr in newTable.columns:
        columns[attr] = ("ocel:ovmap", attr)
    
    newTable.rename(columns=columns, inplace=True)
    newTable[("ocel:type", "ocel:type")] = objType
    newTable.columns = pd.MultiIndex.from_tuples(newTable.columns)

    # reorder columns
    newTable = newTable[[("ocel:type", "ocel:type")] + list(newTable.drop(columns=[("ocel:type", "ocel:type")]).columns)]
    
    return newTable




# saves all tables in OCEL_Models directory: 
#    format: OCEL_Models is root folder, contains folder for data_model. 
#            data_model folder contains a folder for each activity table in Celonis with an event and object table
class OCEL_Model:
    def __init__(self, newFolderName, ocels=None, obj_relation=None):
        self.rootFolder = "OCEL_Models"
        newPath = os.path.join(self.rootFolder, newFolderName)
        
        # if directory for new ocel_model already exists, delete old directory, create new one
        if os.path.exists(newPath):
            shutil.rmtree(newPath)
        os.mkdir(newPath)
        
        self.folder = newPath # save dataframes as pql here
        self.ocels = ocels if ocels is not None else set() # format: set(name1, name2, ...)
        self.obj_relation = obj_relation if obj_relation is not None else set()
        self.objRelationDict = None
    

    def calcObjRelationDict(self):
        # group object relations by object, this can be better in some use cases
        df = pd.DataFrame(self.getRelation())
        df[1] = df[1].apply(lambda x : [x])
        df = pd.DataFrame(df.groupby(0)[1].apply(sum))
        df.reset_index(inplace=True)
        df.columns = ["Object", "Related Objects"]
        df.index = df["Object"]
        self.objRelationDict = df.to_dict()["Related Objects"]

    def getObjRelationDict(self):
        if self.objRelationDict is None:
            self.calcObjRelationDict()
        return self.objRelationDict

    def addEventObjectDf(self, name, eventsDf, objectsDf):

        # make sure events and objects dataframes are aligned (no conflicts in which objects mentioned where...)
        eventsDf, objectsDf = self.alignEventsObjectsBeforeAdding(eventsDf, objectsDf)

        # drop empty columns
        eventsDf.replace('nan', np.nan, inplace=True)
        objectsDf.replace('nan', np.nan, inplace=True)
        eventsDf.dropna(how='all', axis=1, inplace=True)
        objectsDf.dropna(how='all', axis=1, inplace=True)

        if len(eventsDf) == 0 or len(objectsDf) == 0:
            raise EmptyLogException('Event log empty')

        # convert possible values to numeric
        for col in eventsDf.columns:
            eventsDf[col] = pd.to_numeric(eventsDf[col], errors="ignore")
        for col in objectsDf.columns:
            objectsDf[col] = pd.to_numeric(objectsDf[col], errors="ignore")
        
        # convert timestamp column to datetime
        eventsDf[("ocel:timestamp", "ocel:timestamp")] = pd.to_datetime(eventsDf[("ocel:timestamp", "ocel:timestamp")])

        newPath = os.path.join(self.folder, name)
        
        # remove if exists already
        if os.path.exists(newPath):
            shutil.rmtree(newPath)
        os.mkdir(newPath)
        
        # reset index of events dataframe and sort on timestamp
        eventsDf = eventsDf.sort_values(by=[("ocel:timestamp", "ocel:timestamp"), ("ocel:activity", "ocel:activity")]).reset_index(drop=True)
        
        # ensure columsn in right order
        columns = [("ocel:omap", "ocel:omap"), ("ocel:activity", "ocel:activity"), ("ocel:timestamp", "ocel:timestamp")]
        columns = columns + list(set(eventsDf.columns).difference(columns))
        eventsDf = eventsDf[columns]

        # drop duplicate objects
        objectsDf = objectsDf[~objectsDf.index.duplicated(keep='first')]
        
        eventsDf.to_pickle(os.path.join(newPath, "eventsDf.pkl"))
        objectsDf.to_pickle(os.path.join(newPath, "objectsDf.pkl"))            
        
        self.ocels.add(name)

        return True

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
        
        objectsDf = objectsDf[~objectsDf.index.duplicated(keep='first')]
        
        objectsDf.to_pickle(os.path.join(newPath, "objectsDf.pkl"))

        self.ocels.add(name)
        
    def alignEventsObjectsBeforeAdding(self, eventsDf, objectsDf):
        # remove objects that aren't mentioned in any events
        # remove objects from events that aren't mentioned in objectsDf

        objectsDf = copy.deepcopy(objectsDf)

        eventsDf.reset_index(inplace=True, drop=True)

        objectsDf = objectsDf[~objectsDf.index.duplicated(keep='first')]
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
        
        return (eventsDf, objectsDf)
        
        
    def removeOCEL(self, name):
        if name not in self.ocels:
            return True
        filePath = os.path.join(self.folder, name)
        if os.path.exists(filePath):
            shutil.rmtree(filePath)
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
            return set([attr for attr in eventsDf["ocel:vmap"].columns])
        return set()
    
    def getObjectAttributes(self, name):
        objectsDf = self.getObjectsDf(name)
        if "ocel:ovmap" in objectsDf.columns:
            return set([attr for attr in objectsDf["ocel:ovmap"].columns])
        return set()
        
    def setRelation(self, relation):
        self.obj_relation = relation
    
    def getRelation(self):
        return self.obj_relation
    
    def addToRelation(self, objRelationships):
        self.obj_relation = self.obj_relation.union(objRelationships)
    
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
                        value = row[multiColumn[0]][attrKey]
                        if value is not np.nan:
                            innerdict[attrKey] = str(value)
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
        eventsDf = self.transformDictToDf(ocel["ocel:events"])
        eventsDf[("ocel:timestamp", "ocel:timestamp")] = pd.to_datetime(eventsDf[("ocel:timestamp", "ocel:timestamp")])

        objectsDf = self.transformDictToDf(ocel["ocel:objects"])
        
        return (eventsDf, objectsDf)

    
    ############################   OPERATORS:   ############################

    
    def importOCEL(self, path, addObjectRelations=False, newName=""):
        eventsDf, objectsDf = self.transformOcelToEventDfObjectDf(path,ocel=False)

        # prepend objects with object types to avoid same object identifiers referring to different objects (with different type)
        # only do so if objects aren't prefixed with type already:
        if False in list(objectsDf.index.map(lambda x : x.split(":")[0]) == objectsDf[("ocel:type", "ocel:type")]):
            eventsDf[("ocel:omap", "ocel:omap")] = eventsDf[("ocel:omap", "ocel:omap")].apply(lambda x : [objectsDf.loc[obj][("ocel:type", "ocel:type")] + ":" + obj for obj in x])
            objectsDf.index = objectsDf.index.map(lambda x : objectsDf.loc[x][("ocel:type", "ocel:type")] + ":" + x)

        # align before adding anything to relation
        eventsDf, objectsDf = self.alignEventsObjectsBeforeAdding(eventsDf, objectsDf)

        toAddedRelations = set([(obj, obj) for obj in objectsDf.index])

        if addObjectRelations:
            for objects in eventsDf[("ocel:omap", "ocel:omap")]:
                prod = product(set(objects), set(objects))
                
                toAddedRelations = toAddedRelations.union(prod)

        self.addToRelation(toAddedRelations)
        self.objRelationDict = None

        self.addEventObjectDf(newName, eventsDf, objectsDf)

        return True

        


    # input: 2 ocels, object relationship, activity relationship
    # output: 1 ocel, objects from log2 merged into log1 based on object and activity relation
    def manualMiner(self, name1, name2, activity_relation, mergeEvents=False, newName=""):

        # get logs
        eventsDf1 = self.getEventsDf(name1)
        objectsDf1 = self.getObjectsDf(name1)
        eventsDf2 = self.getEventsDf(name2)
        objectsDf2 = self.getObjectsDf(name2)

        # start from log1 since we want to merge objects from log2 into log1
        newEventsDf = copy.deepcopy(eventsDf1)
        newObjectsDf = copy.deepcopy(objectsDf1)

        missingEventsDf = copy.deepcopy(eventsDf2)

        object_relation = self.getObjRelationDict()

        # keep track of all added objects
        allAddedObjects = set()

        for pair in activity_relation:
            leftAct = pair[0]
            rightAct = pair[1]
            leftOccurences = eventsDf1[eventsDf1[("ocel:activity", "ocel:activity")] == leftAct].index
            rightOccurences = eventsDf2[eventsDf2[("ocel:activity", "ocel:activity")] == rightAct].index
            rightObjects = set()
            for i in rightOccurences:
                rightObjects = rightObjects.union(eventsDf2.loc[i][("ocel:omap", "ocel:omap")])

            thisRoundAddedObjects = set()
            for leftOcc in leftOccurences:
                toBeAddedObj = set()
                for leftObj in eventsDf1.loc[leftOcc][("ocel:omap", "ocel:omap")]:
                    intersec = rightObjects.intersection(object_relation[leftObj])
                    allAddedObjects = allAddedObjects.union(intersec)
                    toBeAddedObj = toBeAddedObj.union(intersec)
                    thisRoundAddedObjects = thisRoundAddedObjects.union(intersec)

                if toBeAddedObj != set():
                    newEventsDf.at[leftOcc, ("ocel:omap", "ocel:omap")] = list(toBeAddedObj.union(newEventsDf.loc[leftOcc][("ocel:omap", "ocel:omap")]))
            
            # in case we want to merge events, we remove merged objects from their events
            if mergeEvents and thisRoundAddedObjects != set():
                for i in rightOccurences:
                    missingEventsDf.at[i, ("ocel:omap", "ocel:omap")] = list(set(missingEventsDf.at[i, ("ocel:omap", "ocel:omap")]).difference(thisRoundAddedObjects))


        # in case we want to merge events, add events from log2 which were not merged to the new log
        if mergeEvents:
            newEventsDf = pd.concat([newEventsDf, missingEventsDf])
            newObjectsDf = pd.concat([objectsDf1, objectsDf2])
        else:
            # add new objects from log2 to log1
            toBeAddedObjects = list(allAddedObjects.difference(objectsDf1.index))
            newObjectsDf = pd.concat([objectsDf1, objectsDf2.loc[toBeAddedObjects]])

        # if no new name given, create own
        if newName == "":
            newName = "MANUAL_MINER(" + name1 + "," + name2 + ")"

        return self.addEventObjectDf(newName, newEventsDf, newObjectsDf)


    
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

        return self.addEventObjectDf(newName, newEventsDf, newObjectsDf)    

    
    # aggregate operator (merge objects of events with same activty / timestamp into first occurence)
    def aggregate(self, name, aggregateBy=[("ocel:activity", "ocel:activity"), ("ocel:timestamp", "ocel:timestamp")], newName=""):
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)

        aggregateBy = list(set(aggregateBy))

        omap = eventsDf.groupby(aggregateBy, dropna=False)[[("ocel:omap", "ocel:omap")]].apply(sum).reset_index()
        newEventsDf = eventsDf.groupby(aggregateBy, dropna=False).first().reset_index()
        
        newEventsDf[("ocel:omap", "ocel:omap")] = omap[("ocel:omap", "ocel:omap")]
        
        # reorder columns
        columns = [("ocel:omap", "ocel:omap"), ("ocel:activity", "ocel:activity"), ("ocel:timestamp", "ocel:timestamp")]
        columns = columns + list(set(newEventsDf.columns).difference(columns))
        newEventsDf = newEventsDf[columns]
                
        # if no new name given, create own
        if newName == "":
            newName = "AGGREGATE(" + name + ")"

        return self.addEventObjectDf(newName, newEventsDf, objectsDf)

    
    # union operator (merge objects of events with same activty / timestamp)
    # for attribute values, we take values of first log
    def union(self, name1, name2, matchOn={("ocel:timestamp", "ocel:timestamp"): ("ocel:timestamp", "ocel:timestamp"), ("ocel:activity", "ocel:activity"): ("ocel:activity", "ocel:activity")}, respectObjRelations=True, mergeEvents=False, newName=""):

        eventsDf1 = self.getEventsDf(name1)
        objectsDf1 = self.getObjectsDf(name1)
        eventsDf2 = self.getEventsDf(name2)
        objectsDf2 = self.getObjectsDf(name2)

        newEventsDf = copy.deepcopy(eventsDf1)

        missingEventsDf = copy.deepcopy(eventsDf2)
        object_relation = self.getObjRelationDict()

        # re-fromat dataframes so that we only have important columns and no multi-index columsn
        eventsDf1 = eventsDf1[[("ocel:omap", "ocel:omap")] + list(set(matchOn.keys()))]
        eventsDf2 = eventsDf2[[("ocel:omap", "ocel:omap")] + list(set(matchOn.values()))]
        eventsDf1.columns = eventsDf1.columns.droplevel(0)
        eventsDf2.columns = eventsDf2.columns.droplevel(0)
        eventsDf1.reset_index(inplace=True)
        eventsDf2.reset_index(inplace=True)
        eventsDf2.rename(columns={"index": "index_y"}, inplace=True)
        eventsDf2["index_y"] = eventsDf2["index_y"].apply(lambda x : [x])

        left_on = [column[1] for column in matchOn.keys()]
        right_on = [column[1] for column in matchOn.values()]

        # merge based on matching activity names and timestamps
        df = pd.merge(eventsDf1, eventsDf2, left_on=left_on, right_on=right_on).groupby("index", dropna=False)[["ocel:omap_x", "ocel:omap_y", "index_y"]].apply(sum)

        if len(df) > 0:
            for index, row in df.iterrows():
                toBeAddedObjects = set()

                if respectObjRelations:
                    for obj in row["ocel:omap_x"]:
                        intersec = set(row["ocel:omap_y"]).intersection(object_relation[obj])
                        toBeAddedObjects = toBeAddedObjects.union(intersec)
                else:
                    toBeAddedObjects = set(row["ocel:omap_y"])

                if toBeAddedObjects != set():
                    # add merged objects to events of first log
                    newEventsDf.at[index, ("ocel:omap", "ocel:omap")] = list(toBeAddedObjects.union(newEventsDf.loc[index][("ocel:omap", "ocel:omap")]))

                    # remove objects from events in case we want to merge events
                    if mergeEvents:
                        for i in row["index_y"]:
                            missingEventsDf.at[i, ("ocel:omap", "ocel:omap")] = list(set(missingEventsDf.at[i, ("ocel:omap", "ocel:omap")]).difference(toBeAddedObjects))

        # in case we want to merge events, add events from log2 which were not merged to the new log
        if mergeEvents:
            newEventsDf = pd.concat([newEventsDf, missingEventsDf])

        if newName == "":
            newName = "UNION(" + name1 + "," + name2 + ")"

        return self.addEventObjectDf(newName, newEventsDf, pd.concat([objectsDf1, objectsDf2]))



    def difference(self, name1, name2, matchOn={("ocel:timestamp", "ocel:timestamp"): ("ocel:timestamp", "ocel:timestamp"), ("ocel:activity", "ocel:activity"): ("ocel:activity", "ocel:activity")}, newName=""):

        # get logs
        eventsDf1 = self.getEventsDf(name1)
        objectsDf1 = self.getObjectsDf(name1)
        eventsDf2 = self.getEventsDf(name2)
        objectsDf2 = self.getObjectsDf(name2)

        newEventsDf = copy.deepcopy(eventsDf1)

        # first group by timestamp and activity
        eventsDf2 = eventsDf2.groupby(list(set(matchOn.values())), dropna=False)[[("ocel:omap", "ocel:omap")]].apply(sum)

        # join dataframes based on activity and timestamps
        joined = pd.merge(eventsDf1, eventsDf2, how="left", left_on=list(matchOn.keys()), right_on=list(matchOn.values()))
        
        # remove objects from second log from first log
        newEventsDf[("ocel:omap", "ocel:omap")] = joined.apply(lambda r: list(set(r[("ocel:omap_x", "ocel:omap_x")]).difference(r[("ocel:omap_y", "ocel:omap_y")])) if not r[[("ocel:omap_x", "ocel:omap_x"), ("ocel:omap_y", "ocel:omap_y")]].isnull().values.any() else r[("ocel:omap_x", "ocel:omap_x")], axis=1)

        newObjectsDf = pd.concat([objectsDf1, objectsDf2])

        # if no new name given, create own
        if newName == "":
            newName = "DIFFERENCE(" + name1 + "," + name2 + ")"

        return self.addEventObjectDf(newName, newEventsDf, newObjectsDf)



    def intersection(self, name1, name2, matchOn={("ocel:timestamp", "ocel:timestamp"): ("ocel:timestamp", "ocel:timestamp"), ("ocel:activity", "ocel:activity"): ("ocel:activity", "ocel:activity")}, newName=""):

        # get logs
        eventsDf1 = self.getEventsDf(name1)
        objectsDf1 = self.getObjectsDf(name1)
        eventsDf2 = self.getEventsDf(name2)
        objectsDf2 = self.getObjectsDf(name2)

        newEventsDf = copy.deepcopy(eventsDf1)

        # first group by timestamp and activity
        eventsDf2 = eventsDf2.groupby(list(set(matchOn.values())), dropna=False)[[("ocel:omap", "ocel:omap")]].apply(sum)

        # join dataframes based on activity and timestamps
        joined = pd.merge(eventsDf1, eventsDf2, how="left", left_on=list(matchOn.keys()), right_on=list(matchOn.values()))
        
        # remove objects from second log from first log
        newEventsDf[("ocel:omap", "ocel:omap")] = joined.apply(lambda r: list(set(r[("ocel:omap_x", "ocel:omap_x")]).intersection(r[("ocel:omap_y", "ocel:omap_y")])) if not r[[("ocel:omap_x", "ocel:omap_x"), ("ocel:omap_y", "ocel:omap_y")]].isnull().values.any() else [], axis=1)

        newObjectsDf = pd.concat([objectsDf1, objectsDf2])

        # if no new name given, create own
        if newName == "":
            newName = "INTERSECTION(" + name1 + "," + name2 + ")"

        return self.addEventObjectDf(newName, newEventsDf, newObjectsDf)

        


    # flattening operator that transforms all events to one object notion
    def flatten(self, name, objectType, newName=""):

        # get logs
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)    

        newEventsDf = copy.deepcopy(eventsDf)
        newObjectsDf = copy.deepcopy(objectsDf)

        object_relation = self.getObjRelationDict()

        # find all objects of type objectType
        allObjects = set(objectsDf[objectsDf[("ocel:type", "ocel:type")] == objectType].index)


        for ev_id, event in eventsDf.iterrows():
            relatedObjects = event[("ocel:omap", "ocel:omap")]
            toBeAddedObjects = allObjects.intersection(relatedObjects) # related objects that already are of correct type
            relatedObjects = set(relatedObjects).difference(toBeAddedObjects) # remaining objects

            # check which objects from relatedObjects are in relation with objects from objectType
            for relatedObj in relatedObjects:
                toBeAddedObjects = toBeAddedObjects.union(allObjects.intersection(object_relation[relatedObj]))

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

        return self.addEventObjectDf(newName, newEventsDf, newObjectsDf)    
    


    # filter operator section start ----------------------------------------------------------------------


    # activities: set of activities
    # filter out events that aren't in activities parameter set
    def filterByActivity(self, eventsDf, activities):
        return eventsDf[eventsDf[("ocel:activity", "ocel:activity")].isin(activities)]


    # parameters = {attr : values, ...}
    # type int/float/datetime: values = (min, max)
    # type other: values = set([a,b,c,...])
    def filterEventAttributes(self, name, parameters, newName):

        # get logs
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)

        newEventsDf = copy.deepcopy(eventsDf)

        # first remove non-fitting objects from objectsDf
        for key, values in parameters.items():
            mini = float(values[0])
            maxi = float(values[1])
            
            newEventsDf = newEventsDf[(newEventsDf["ocel:vmap"][key] <= maxi) & (newEventsDf["ocel:vmap"][key] >= mini)]


        # if no new name given, create own
        if newName == "":
            newName = "FILTER_EVENT_ATTRIBUTES(" + name  + ")"

        # reset index of events dataframe
        eventsDf.reset_index(inplace=True, drop=True)

        return self.addEventObjectDf(newName, newEventsDf, objectsDf)



    # parameters = {attr : values, ...}
    # type int/float/datetime: values = (min, max)
    # type other: values = set([a,b,c,...])
    def filterObjectAttributes(self, name, parameters, newName):
        
        # get logs
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)

        newObjectsDf = copy.deepcopy(objectsDf)

        # first remove non-fitting objects from objectsDf
        for key, values in parameters.items():
            mini = float(values[0])
            maxi = float(values[1])
            newObjectsDf = newObjectsDf[(newObjectsDf["ocel:ovmap"][key] <= maxi) & (newObjectsDf["ocel:ovmap"][key] >= mini)]
            

        # if no new name given, create own
        if newName == "":
            newName = "FILTER_OBJECT_ATTRIBUTES(" + name  + ")"

        # reset index of events dataframe
        eventsDf.reset_index(inplace=True, drop=True)

        return self.addEventObjectDf(newName, eventsDf, newObjectsDf)




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


    def filterByObjectType(self, eventsDf, objectsDf, objectTypes):
        objectTypes = set(objectTypes)

        # get objects with specified object types
        allowedObjects = set(objectsDf[objectsDf[("ocel:type", "ocel:type")].isin(objectTypes)].index)

        return self.filterByObject(eventsDf, allowedObjects)



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

        if mode == "Event Attributes":
            return self.filterEventAttributes(name, parameters, newName)
        elif mode == "Object Attributes":
            return self.filterObjectAttributes(name, parameters, newName)
        
        else:
            # get logs
            eventsDf = self.getEventsDf(name)
            objectsDf = self.getObjectsDf(name)    

            newEventsDf = copy.deepcopy(eventsDf)
        
            if mode == "Activities":
                newEventsDf = self.filterByActivity(newEventsDf, parameters)
            elif mode == "Objects":
                newEventsDf = self.filterByObject(newEventsDf, parameters)
            elif mode == "Object Types":
                newEventsDf = self.filterByObjectType(newEventsDf, objectsDf, parameters)
            elif mode == "Timestamps":
                newEventsDf = self.filterByTimestamp(newEventsDf, parameters)
            # reset index of events dataframe
            newEventsDf.reset_index(inplace=True, drop=True)

            # if no new name given, create own
            if newName == "":
                newName = "FILTER(" + name + ")"

            return self.addEventObjectDf(newName, newEventsDf, objectsDf)

    

    # interleaved miner section start ----------------------------------------------------------------------
        
    def interleavedMiner(self, name1, name2, mergeEvents=False, newName=""):

        newEventsDf = self.getEventsDf(name1)

        newEventsDf1 = copy.deepcopy(newEventsDf)
        newEventsDf2 = self.getEventsDf(name2)

        missingEventsDf = copy.deepcopy(newEventsDf2)

        objectsDf1 = self.getObjectsDf(name1)    
        objectsDf2 = self.getObjectsDf(name2)    

        object_relation = self.getObjRelationDict()

        newEventsDf1[("log", "log")] = 1
        newEventsDf2[("log", "log")] = 2

        # concat both dataframes and order events based on timestamp (but keep track from which log events come)
        tempDf = pd.concat([newEventsDf1, newEventsDf2])[[("ocel:omap", "ocel:omap"), ("ocel:timestamp", "ocel:timestamp"), ("log", "log")]]
        tempDf = tempDf.sort_values(by=[("ocel:timestamp", "ocel:timestamp"), ("log", "log")])

        # keep track of index in original logs
        tempDf.reset_index(inplace=True)
        tempDf[("index", "index")] = tempDf["index"].apply(lambda x: [x])

        # group by timestamp since we want transition from all events in case they have same timestamp
        tempDf = tempDf.groupby([("ocel:timestamp", "ocel:timestamp"), ("log", "log")], dropna=False)[[("ocel:omap", "ocel:omap"), ("index", "index")]].apply(sum)

        allAddedObjects = set()


        # loop through tempDf and keep track of previous index
        # in case we switch to log 2, we merge the objects from that into omap of event referred to in previous index
        previousIndex = None
        for index, row in tempDf.iterrows():
            if previousIndex == None:
                previousIndex = index
            elif index[1] == 2:
                if previousIndex[1] == 1:
                    thisRoundObjects = set()
                    for ev_id in tempDf.loc[previousIndex][("index", "index")]:
                        toBeAddedObjects = set()
                        for obj1 in newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]:
                            intersec = set(row[("ocel:omap", "ocel:omap")]).intersection(object_relation[obj1])
                            allAddedObjects = allAddedObjects.union(intersec)
                            toBeAddedObjects = toBeAddedObjects.union(intersec)
                            thisRoundObjects = thisRoundObjects.union(intersec)
                        newEventsDf.at[ev_id, ("ocel:omap", "ocel:omap")] = list(toBeAddedObjects.union(newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]))
                    # remove objects from events in case we want to merge events
                    if mergeEvents:
                        for i in row[("index", "index")]:
                            missingEventsDf.at[i, ("ocel:omap", "ocel:omap")] = list(set(missingEventsDf.at[i, ("ocel:omap", "ocel:omap")]).difference(thisRoundObjects))

            previousIndex = index

        # in case we want to merge events, add events from log2 which were not merged to the new log
        if mergeEvents:
            newEventsDf = pd.concat([newEventsDf, missingEventsDf])
            newObjectsDf = pd.concat([objectsDf1, objectsDf2])
        else:
            # add new objects from log2 to log1
            toBeAddedObjects = list(allAddedObjects.difference(objectsDf1.index))
            newObjectsDf = pd.concat([objectsDf1, objectsDf2.loc[toBeAddedObjects]])

        # if no new name given, create own
        if newName == "":
            newName = "INTERLEAVED_MINER(" + name1 + "," + name2 + ")"

        return self.addEventObjectDf(newName, newEventsDf, newObjectsDf)

    
    
    def nonInterleavedMiner(self, name1, name2, mergeEvents=False, newName=""):

        newEventsDf = self.getEventsDf(name1)

        newEventsDf1 = copy.deepcopy(newEventsDf)
        newEventsDf2 = self.getEventsDf(name2)

        missingEventsDf = copy.deepcopy(newEventsDf2)

        objectsDf1 = self.getObjectsDf(name1) 
        objectsDf2 = self.getObjectsDf(name2) 

        object_relation = self.getObjRelationDict()

        newEventsDf1[("log", "log")] = 1
        newEventsDf2[("log", "log")] = 2

        # concat both dataframes and order events based on timestamp (but keep track from which log events come)
        tempDf = pd.concat([newEventsDf1, newEventsDf2])[[("ocel:omap", "ocel:omap"), ("ocel:timestamp", "ocel:timestamp"), ("log", "log")]]
        tempDf = tempDf.sort_values(by=[("ocel:timestamp", "ocel:timestamp"), ("log", "log")])

        # keep track of index in original logs
        tempDf.reset_index(inplace=True)
        tempDf[("index", "index")] = tempDf["index"].apply(lambda x: [x])

        # group by timestamp since we want transition from all events in case they have same timestamp
        tempDf = tempDf.groupby([("ocel:timestamp", "ocel:timestamp"), ("log", "log")], dropna=False)[[("ocel:omap", "ocel:omap"), ("index", "index")]].apply(sum)

        allAddedObjects = set()

        # loop through tempDf and keep track of previous index
        # in case we switch to log 2, we merge the objects from that into omap of event referred to in previous index
        previousIndex = None
        for i in range(1, len(tempDf)-1):
            previousIndex = tempDf.index[i-1]
            currentIndex = tempDf.index[i]
            nextIndex = tempDf.index[i+1]

            row = tempDf.loc[currentIndex]

            if currentIndex[1] == 2:
                if previousIndex[1] == 1 and nextIndex[1] == currentIndex[1]:
                    thisRoundObjects = set()
                    for ev_id in tempDf.loc[previousIndex][("index", "index")]:
                        toBeAddedObjects = set()
                        for obj1 in newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]:
                            intersec = set(row[("ocel:omap", "ocel:omap")]).intersection(object_relation[obj1])
                            allAddedObjects = allAddedObjects.union(intersec)
                            toBeAddedObjects = toBeAddedObjects.union(intersec)
                            thisRoundObjects = thisRoundObjects.union(intersec)
 
                        newEventsDf.at[ev_id, ("ocel:omap", "ocel:omap")] = list(toBeAddedObjects.union(newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]))
                    # remove objects from events in case we want to merge events
                    if mergeEvents and thisRoundObjects != set():
                        for i in row[("index", "index")]:
                            missingEventsDf.at[i, ("ocel:omap", "ocel:omap")] = list(set(missingEventsDf.at[i, ("ocel:omap", "ocel:omap")]).difference(thisRoundObjects))

        # in case we want to merge events, add events from log2 which were not merged to the new log
        if mergeEvents:
            newEventsDf = pd.concat([newEventsDf, missingEventsDf])
            newObjectsDf = pd.concat([objectsDf1, objectsDf2])
        else:
            # add new objects from log2 to log1
            toBeAddedObjects = list(allAddedObjects.difference(objectsDf1.index))
            newObjectsDf = pd.concat([objectsDf1, objectsDf2.loc[toBeAddedObjects]])

        # if no new name given, create own
        if newName == "":
            newName = "NONINTERLEAVED_MINER(" + name1 + "," + name2 + ")"

        return self.addEventObjectDf(newName, newEventsDf, newObjectsDf)


    # onlyMergeClosest: instead of merging objects of predecessor events and successor events in log2, we only merge closest one
    def closestTimestamps(self, name1, name2, onlyMergeClosest=True, considerObjRelations=False, mergeEvents=False, newName=""):

        newEventsDf = self.getEventsDf(name1)

        newEventsDf1 = copy.deepcopy(newEventsDf)
        newEventsDf2 = self.getEventsDf(name2)

        missingEventsDf = copy.deepcopy(newEventsDf2)

        objectsDf1 = self.getObjectsDf(name1)    
        objectsDf2 = self.getObjectsDf(name2)    

        object_relation = self.getObjRelationDict()

        newEventsDf1[("log", "log")] = 1
        newEventsDf2[("log", "log")] = 2

        # concat both dataframes and order events based on timestamp (but keep track from which log events come)
        tempDf = pd.concat([newEventsDf1, newEventsDf2])[[("ocel:omap", "ocel:omap"), ("ocel:timestamp", "ocel:timestamp"), ("log", "log")]]
        tempDf = tempDf.sort_values(by=[("ocel:timestamp", "ocel:timestamp"), ("log", "log")])

        # keep track of index in original logs
        tempDf.reset_index(inplace=True)
        tempDf[("index", "index")] = tempDf["index"].apply(lambda x: [x])

        # group by timestamp since we want transition from all events in case they have same timestamp
        tempDf = tempDf.groupby([("ocel:timestamp", "ocel:timestamp"), ("log", "log")], dropna=False)[[("ocel:omap", "ocel:omap"), ("index", "index")]].apply(sum)

        allAddedObjects = set()
        
        # loop through tempDf and keep track of previous index
        # in case we switch to log 2, we merge the objects from that into omap of event referred to in previous index
        previousIndex = None
        counter = 0
        for index, row in tempDf.iterrows():
            before = False
            after = False
            counter += 1
            if previousIndex == None:
                previousIndex = index
            if index[1] == 2:
                if previousIndex[1] == 1:
                    before = True
                else:
                    time = previousIndex[0]
                    if len(tempDf.loc[time]) > 1:
                        before = True
                        previousIndex = (time, 1)
                        row = tempDf.loc[previousIndex]
                        
                if counter < len(tempDf) - 1:
                    nextIndex = tempDf.index[counter]
                    if nextIndex[1] == 1:
                        after = True
                        
                        if onlyMergeClosest:
                            if previousIndex[1] == 1:
                                timeBefore = index[0] - previousIndex[0]
                                timeAfter = nextIndex[0] - index[0]
                                if timeBefore == timeAfter:
                                    before = True
                                    after = True
                                elif timeBefore < timeAfter:
                                    after = False
                                else:
                                    before = False

                if before:
                    thisRoundObjects = set()
                    for ev_id in tempDf.loc[previousIndex][("index", "index")]:
                        toBeAddedObjects = set()
                        if considerObjRelations:
                            for obj1 in newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]:
                                intersec = set(row[("ocel:omap", "ocel:omap")]).intersection(object_relation[obj1])
                                allAddedObjects = allAddedObjects.union(intersec)
                                toBeAddedObjects = toBeAddedObjects.union(intersec)
                                thisRoundObjects = thisRoundObjects.union(intersec)
                        else:
                            objects = set(row[("ocel:omap", "ocel:omap")])
                            allAddedObjects = allAddedObjects.union(objects)
                            toBeAddedObjects = toBeAddedObjects.union(objects)
                            thisRoundObjects = thisRoundObjects.union(objects)
                        newEventsDf.at[ev_id, ("ocel:omap", "ocel:omap")] = list(toBeAddedObjects.union(newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]))
                    # remove objects from events in case we want to merge events
                    if mergeEvents:
                        for i in row[("index", "index")]:
                            missingEventsDf.at[i, ("ocel:omap", "ocel:omap")] = list(set(missingEventsDf.at[i, ("ocel:omap", "ocel:omap")]).difference(thisRoundObjects))

                if after:
                    thisRoundObjects = set()
                    for ev_id in tempDf.loc[nextIndex][("index", "index")]:
                        toBeAddedObjects = set()
                        if considerObjRelations:
                            for obj1 in newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]:
                                intersec = set(row[("ocel:omap", "ocel:omap")]).intersection(object_relation[obj1])
                                allAddedObjects = allAddedObjects.union(intersec)
                                toBeAddedObjects = toBeAddedObjects.union(intersec)
                                thisRoundObjects = thisRoundObjects.union(intersec)
                        else:
                            objects = set(row[("ocel:omap", "ocel:omap")])
                            allAddedObjects = allAddedObjects.union(objects)
                            toBeAddedObjects = toBeAddedObjects.union(objects)
                            thisRoundObjects = thisRoundObjects.union(objects)
                        newEventsDf.at[ev_id, ("ocel:omap", "ocel:omap")] = list(toBeAddedObjects.union(newEventsDf.loc[ev_id][("ocel:omap", "ocel:omap")]))
                    # remove objects from events in case we want to merge events
                    if mergeEvents:
                        for i in row[("index", "index")]:
                            missingEventsDf.at[i, ("ocel:omap", "ocel:omap")] = list(set(missingEventsDf.at[i, ("ocel:omap", "ocel:omap")]).difference(thisRoundObjects))
                            
            previousIndex = index

        # in case we want to merge events, add events from log2 which were not merged to the new log
        if mergeEvents:
            newEventsDf = pd.concat([newEventsDf, missingEventsDf])
            newObjectsDf = pd.concat([objectsDf1, objectsDf2])
        else:
            # add new objects from log2 to log1
            toBeAddedObjects = list(allAddedObjects.difference(objectsDf1.index))
            newObjectsDf = pd.concat([objectsDf1, objectsDf2.loc[toBeAddedObjects]])

        # if no new name given, create own
        if newName == "":
            newName = "CLOSEST_TIMESTAMPS(" + name1 + "," + name2 + ")"
            
        return self.addEventObjectDf(newName, newEventsDf, newObjectsDf)




# ------------------------- Event Recipe Operator -------------------------------------

    def matchingEvents(self, sequence, objectsDf, eventsDf):
        boolEvents = []
        for index, ev in eventsDf.iterrows():
            needNew = True
            omap = ev[("ocel:omap", "ocel:omap")]
            activity = ev[("ocel:activity", "ocel:activity")]
            
            # find object types related to event
            types = set()
            for obj in omap:
                types.add(objectsDf.loc[obj][("ocel:type", "ocel:type")])
                    
            # check if event matches filter criteria
            for seqEv in sequence:
                if seqEv["activity"] == activity:
                    if "objectTypes" in seqEv:
                        if seqEv["objectTypes"].issubset(types):
                            boolEvents.append(True)
                            needNew = False
                            break
                    else:
                        boolEvents.append(True)
                        needNew = False
                        break
            
            # if filter criteria not met, append False
            if needNew:
                boolEvents.append(False)
                
        return boolEvents


    def matchesSequenceEvent(self, sequence, i, objectsDf, event):
        compareEvent = sequence[i]
        # find object types related to event
        if compareEvent["activity"] == event[("ocel:activity", "ocel:activity")]:
            types = set()
            if "objectTypes" not in compareEvent:
                return True
            else:
                for obj in event[("ocel:omap", "ocel:omap")]:
                    types.add(objectsDf.loc[obj][("ocel:type", "ocel:type")])

                if compareEvent["objectTypes"].issubset(types):
                    return True
        return False

    def directlySequence(self, name, newActivityName, sequence, time=timedelta.max, matchOnObjectTypes=set(), matchOnAttributes=set(), findAll=False):
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)
            
        # drop all events that don't match any of the filter criteria (activity, object types)
        keys = set()
        for dict in sequence:
            keys = keys.union(dict.keys())
        if "objectTypes" in keys:
            filteredDf = eventsDf[self.matchingEvents(sequence, objectsDf, eventsDf)]
        # in case no object type filter was specified, this is faster
        else:
            filteredDf = eventsDf[eventsDf[("ocel:activity", "ocel:activity")].isin([dict["activity"] for dict in sequence])]
            
        # find sequence of desired activities
        activitySequence = [ev["activity"] for ev in sequence]
        seqLength = len(activitySequence)
        seqFilter = True
        for i in range(seqLength):
            act = activitySequence[i]
            seqFilter &= pd.DataFrame(filteredDf[("ocel:activity", "ocel:activity")]).shift(-i).eq(act).any(1) 
        
        # startOfSeqDf contains first events of each potential sequence occurence (need to filter further)
        startOfSeqIndexes = list(filteredDf[seqFilter].index)
        
        # filter based on passed time (and directly follows relation) and object relations
        toDrop = []
        for startIndex in startOfSeqIndexes:
            if startIndex in toDrop:
                continue
            startTime = filteredDf.loc[startIndex][("ocel:timestamp", "ocel:timestamp")]
            endIndex = filteredDf.loc[startIndex:].index[seqLength-1]
            endTime = filteredDf.loc[endIndex][("ocel:timestamp", "ocel:timestamp")]
            # in case of default parameter, don't check
            if timedelta.max != time:
                if endTime - startTime > time:
                    toDrop.append(startIndex)
                    continue
                
            # because of directly follows relation, last index of sequence has to be exactly greater by length of seq
            if endIndex - startIndex != seqLength-1:
                toDrop.append(startIndex)
                continue

            # check for matching objects in sequence
            usedEvents = []
            objects = set(filteredDf.loc[startIndex][("ocel:omap", "ocel:omap")])
            for i in range(1, seqLength):
                index = filteredDf.loc[startIndex:].index[i]
                
                # in case matchOnAttributes specified, we drop startIndex if we encounter event with unmatching attribute values
                if matchOnAttributes != set():
                    for attr in matchOnAttributes:
                        if filteredDf.loc[index][("ocel:vmap", attr)] != filteredDf.loc[startIndex][("ocel:vmap", attr)]:
                            toDrop.append(startIndex)
                            break
                
                usedEvents.append(index)
                # use intersection since we want matching events
                objects = objects.intersection(filteredDf.loc[index][("ocel:omap", "ocel:omap")])
            types = set(objectsDf.loc[list(objects)][("ocel:type", "ocel:type")])
            if not matchOnObjectTypes.issubset(types):
                toDrop.append(startIndex)
            # in case we don't want to find all occurences of the sequence, but instead only the first one, we can exclude already used startIndexes
            elif not findAll:
                for index in usedEvents:
                    if index in startOfSeqIndexes:
                        toDrop.append(index)
                
        for index in toDrop:
            startOfSeqIndexes.remove(index)

        newEventsDf = copy.deepcopy(eventsDf)
        
        # create new event based on old events in sequence and remove old ones    
        for startIndex in startOfSeqIndexes:
            objects = set(eventsDf.loc[startIndex][("ocel:omap", "ocel:omap")])
            for i in range(1, seqLength):
                objects = objects.union(eventsDf.loc[startIndex+i][("ocel:omap", "ocel:omap")])
            
            # create new event based on last event in sequence, merge all objects into omap, update activity name
            newEvent = copy.deepcopy(newEventsDf.loc[startIndex+seqLength-1])
            newEvent[("ocel:omap", "ocel:omap")] = list(objects)
            newEvent[("ocel:activity", "ocel:activity")] = newActivityName
            newEvent = pd.DataFrame(newEvent).T
            newEventsDf = pd.concat([newEventsDf, newEvent], ignore_index=True)
        
        # drop remaining events
        toDrop = set()
        for startIndex in startOfSeqIndexes:
            for i in range(seqLength):
                toDrop.add(startIndex+i)
        newEventsDf.drop(list(toDrop), inplace=True)
                
        newEventsDf = newEventsDf.sort_values(by=[("ocel:timestamp", "ocel:timestamp"), ("ocel:activity", "ocel:activity")]).reset_index(drop=True)
        
        return newEventsDf


    def eventuallySequence(self, name, newActivityName, sequence, time=timedelta.max, matchOnObjectTypes=set(), matchOnAttributes=set(), findAll=False):     
        eventsDf = self.getEventsDf(name)
        objectsDf = self.getObjectsDf(name)
            
        # drop all events that don't match any of the filter criteria (activity, object types)
        keys = set()
        for dict in sequence:
            keys = keys.union(dict.keys())
        if "objectTypes" in keys:
            filteredDf = eventsDf[self.matchingEvents(sequence, objectsDf, eventsDf)]
        # in case no object type filter was specified, this is faster
        else:
            filteredDf = eventsDf[eventsDf[("ocel:activity", "ocel:activity")].isin([dict["activity"] for dict in sequence])]
            
        seqLength = len(sequence)
        startOfSeqDf = filteredDf[self.matchingEvents(sequence[0:1], objectsDf, filteredDf)]
            
        allEvents = set()
        groupedEvents = []
        for startIndex, firstEvent in startOfSeqDf.iterrows():
            if startIndex in allEvents:
                continue
            lastIndex = startIndex
            objects = set(firstEvent[("ocel:omap", "ocel:omap")])
            groupEvents = [startIndex]
            minimumIndex = 1

            # create copy of df to work on
            filteredSliceDf = copy.deepcopy(filteredDf)
            # only consider subset of dataframe that fits into desired timeframe
            # but only if time is not the default parameter
            if time != timedelta.max:
                startTime = firstEvent[("ocel:timestamp", "ocel:timestamp")]
                endTime = startTime + time
                filteredSliceDf = filteredSliceDf[(filteredSliceDf[("ocel:timestamp", "ocel:timestamp")] <= endTime) & (filteredSliceDf[("ocel:timestamp", "ocel:timestamp")] >= startTime)]
            # in case attributes to match on are given, only consider subset of dataframe with same values as firstEvent in sequence
            if matchOnAttributes != set():
                for attr in matchOnAttributes:
                    filteredSliceDf = filteredSliceDf[filteredSliceDf[("ocel:vmap", attr)] == firstEvent[("ocel:vmap", attr)]]


            # in case of matching object types, only consider subset where intersection of omap in firstEvent is not empty
            if matchOnObjectTypes != set():
                filteredSliceDf[("intersect", "intersect")] = filteredSliceDf[("ocel:omap", "ocel:omap")].apply(lambda row: set(firstEvent[("ocel:omap", "ocel:omap")]).intersection(row))
                filteredSliceDf[("intersect", "intersect")] = filteredSliceDf[("intersect", "intersect")].apply(len)
                filteredSliceDf = filteredSliceDf[filteredSliceDf[("intersect", "intersect")] > 0]

            # we don't want to try finding the pattern more times than theoretical possible sequences exists
            maxLength = 1
            for i in range(seqLength): 
                # start multiplying from back since might be 0 ?
                maxLength *= len(filteredSliceDf[filteredSliceDf[("ocel:activity", "ocel:activity")] == sequence[seqLength-i-1]["activity"]])
            for n in range(maxLength):
                for i in range(minimumIndex, seqLength):
                    if filteredSliceDf.index[-1] == lastIndex:
                        break
                    nextIndex = filteredSliceDf.loc[lastIndex:].index[1]
                    for index, event in filteredSliceDf.loc[nextIndex:].iterrows():
                        if index in allEvents:
                            continue
                        # find first event that matches filter criteria for next event in sequence
                        if self.matchesSequenceEvent(sequence, i, objectsDf, event):
                            # we only care about matching objects if parameter was passed
                            if matchOnObjectTypes == set():
                                groupEvents.append(index)
                                lastIndex = index
                                break
                            else:
                                # check that event has matching object type(s)
                                tempObjects = objects.intersection(event[("ocel:omap", "ocel:omap")])
                                types = set(objectsDf.loc[list(tempObjects)][("ocel:type", "ocel:type")])
                                if matchOnObjectTypes.issubset(types):
                                    objects = tempObjects
                                    groupEvents.append(index)
                                    lastIndex = index
                                    break
                if len(groupEvents) == seqLength:
                    groupedEvents.append(groupEvents)
                    # in case we want to find all sequences of pattern (reusing events allowed), we continue searching
                    if findAll:
                        minimumIndex = len(groupEvents) - 1
                        lastIndex = groupEvents[-1]
                        groupEvents = groupEvents[:-1]
                        objects = set(firstEvent[("ocel:omap", "ocel:omap")])
                        for ev in groupEvents:
                            objects = objects.intersection(filteredDf.loc[ev][("ocel:omap", "ocel:omap")])
                    else:
                        allEvents = allEvents.union(groupEvents)
                        break

                elif len(groupEvents) == 1:
                    break
                # in case we didn't find desired pattern with correct object relationships, we can look for 
                # another variation of same pattern by choosing a different event at an earlier stage in path
                else:
                    minimumIndex = len(groupEvents) - 1
                    lastIndex = groupEvents[-1]
                    groupEvents = groupEvents[:-1]
                    objects = set(firstEvent[("ocel:omap", "ocel:omap")])
                    for ev in groupEvents:
                        objects = objects.intersection(filteredDf.loc[ev][("ocel:omap", "ocel:omap")])                        
                        
        newEventsDf = copy.deepcopy(eventsDf)
        
        # create new event (based on attributes of last occuring event in sequence) and remove old ones    
        for events in groupedEvents:
            objects = set()
            for ev in events:
                objects = objects.union(eventsDf.loc[ev][("ocel:omap", "ocel:omap")])
            # create new event based on last event in sequence, merge all objects into omap, update activity name
            newEvent = copy.deepcopy(newEventsDf.loc[events[-1]])
            newEvent[("ocel:omap", "ocel:omap")] = list(objects)
            newEvent[("ocel:activity", "ocel:activity")] = newActivityName
            newEvent = pd.DataFrame(newEvent).T
            newEventsDf = pd.concat([newEventsDf, newEvent], ignore_index=True)
            
        # drop all old events
        toDrop = set()
        for events in groupedEvents:
            toDrop = toDrop.union(events)
        newEventsDf.drop(list(toDrop), inplace=True)

        newEventsDf = newEventsDf.sort_values(by=[("ocel:timestamp", "ocel:timestamp"), ("ocel:activity", "ocel:activity")]).reset_index(drop=True)
        
        return newEventsDf


    # newActivityName: name of activity of new event
    # sequence: list of event filters [{"activity": "pack item", "objectTypes": set(["CASE_ITEMS"])}, ...]
    # time: allowed time that may pass between first and last event of sequence
    # matchOnObjectTypes: set of object types. If specified, events will only be matched if they have at least one matching object of 
    # all specified types in all events. E.g. set(["items"]) means that all events in sequence need to mention same item
    # findAll: specifies whether we should only look for 1st occurrence of pattern or search for all. In findAll case, "reusing" events is allowed
    # directly: specifies whether events have to be directly followed by each other. Else other events may occur inbetween
    # newName: name of new OCEL
    def eventRecipe(self, name, newActivityName, sequence, time=timedelta.max, matchOnObjectTypes=set(), matchOnAttributes=set(), findAll=False, directly=True, newName=""):
        if directly:
            eventsDf = self.directlySequence(name, newActivityName, sequence, time, matchOnObjectTypes, matchOnAttributes, findAll)
        else:
            eventsDf = self.eventuallySequence(name, newActivityName, sequence, time, matchOnObjectTypes, matchOnAttributes, findAll)
        
        objectsDf = self.getObjectsDf(name)
            
        # if no new name given, create own
        if newName == "":
            newName = "EVENT_RECIPE(" + name + ")"

        return self.addEventObjectDf(newName, eventsDf, objectsDf)
