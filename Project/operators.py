import copy
import json
import ocel as ocel_lib
import datetime


# input: 2 ocels, object relationship, attribute name(s) from ocels
# output: 1 ocel, objects from log2 merged into log1 based on matches in values of passed attribute(s)
# attribute 1 are attribute names from log1, while attribute2 are attribute names from log2
def matchMiner(log1, log2, object_relation, attribute1, attribute2=""):
    if attribute2 == "":
        attribute2 = attribute1
    # start from log1 since we want to merge objects from log2 into log1
    newLog = copy.deepcopy(log1)
    
    # adjust global
    newLog['ocel:global-log']['ocel:object-types'] = list(set(newLog['ocel:global-log']['ocel:object-types']).union(set(log2['ocel:global-log']['ocel:object-types'])))
    newLog['ocel:global-log']['ocel:attribute-names'] = list(set(newLog['ocel:global-log']['ocel:attribute-names']).union(set(log2['ocel:global-log']['ocel:attribute-names'])))



    added_objects = set()
    # find objects in log2 that match attribute value and are in object relation
    # adjust events
    for i in range(len(newLog['ocel:events'])):
        for j in range(len(log2['ocel:events'])):
            if attribute1 in log1['ocel:events'][str(i)]['ocel:vmap'].keys() and attribute2 in log2['ocel:events'][str(j)]['ocel:vmap'].keys():
                if log1['ocel:events'][str(i)]['ocel:vmap'][attribute1] == log2['ocel:events'][str(j)]['ocel:vmap'][attribute2]:
                    for obj1 in newLog['ocel:events'][str(i)]['ocel:omap']:
                        for obj2 in log2['ocel:events'][str(j)]['ocel:omap']:
                            if (obj1, obj2) in object_relation: ####### THIS HAS TO BE ADJUSTED DEPENDING ON FORMAT OF object_relation or format adjusted
                                added_objects.add(obj2)
                                newLog['ocel:events'][str(i)]['ocel:omap'] = list(set(newLog['ocel:events'][str(i)]['ocel:omap']).union([obj2]))
                                # fix vmap
                                for key, value in log2['ocel:events'][str(j)]['ocel:vmap'].items():
                                    if key not in newLog['ocel:events'][str(i)]['ocel:vmap']:
                                        newLog['ocel:events'][str(i)]['ocel:vmap'][key] = value

    # adjust objects
    for obj in added_objects:
        newLog['ocel:objects'][obj] = log2['ocel:objects'][obj] # {'ocel:type': log2['ocel:objects'][obj]['ocel:type'], 'ocel:ovmap': log2['ocel:objects'][obj]['ocel:ovmap'] }
                            
    # validation
    ocel_lib.export_log(newLog, 'oceltest.json')
    if not ocel_lib.validate('oceltest.json', 'schema.json'):
        print(newLog)
        raise Exception("INVALID OCEL DOES NOT MATCH SCHEMA")
        
    print("successful validation of new log")
    
    return newLog

# input: 2 ocels, object relationship, activity relationship
# output: 1 ocel, objects from log2 merged into log1 based on object and activity relation
def manualMiner(log1, log2, object_relation, activity_relation):
    # start from log1 since we want to merge objects from log2 into log1
    newLog = copy.deepcopy(log1)
    
    # adjust global
    newLog['ocel:global-log']['ocel:attribute-names'] = list(set(newLog['ocel:global-log']['ocel:attribute-names']).union(set(log2['ocel:global-log']['ocel:attribute-names'])))
    newLog['ocel:global-log']['ocel:object-types'] = list(set(newLog['ocel:global-log']['ocel:object-types']).union(set(log2['ocel:global-log']['ocel:object-types'])))
    
    added_objects = set()
    # find objects in log2 that match attribute value and are in object relation
    # adjust events
    for i in range(len(newLog['ocel:events'])):
        for j in range(len(log2['ocel:events'])):
            activity1 = log1['ocel:events'][str(i)]['ocel:activity']
            activity2 = log2['ocel:events'][str(j)]['ocel:activity']
            if (activity1, activity2) in activity_relation:
                for obj1 in newLog['ocel:events'][str(i)]['ocel:omap']:
                    for obj2 in log2['ocel:events'][str(j)]['ocel:omap']:
                        if (obj1, obj2) in object_relation: ####### THIS HAS TO BE ADJUSTED DEPENDING ON FORMAT OF object_relation or format adjusted
                            added_objects.add(obj2)
                            newLog['ocel:events'][str(i)]['ocel:omap'] = list(set(newLog['ocel:events'][str(i)]['ocel:omap']).union([obj2]))
                                # fix vmap
                            for key, value in log2['ocel:events'][str(j)]['ocel:vmap'].items():
                                if key not in newLog['ocel:events'][str(i)]['ocel:vmap']:
                                    newLog['ocel:events'][str(i)]['ocel:vmap'][key] = value

    # adjust objects
    for obj in added_objects:
        newLog['ocel:objects'][obj] = log2['ocel:objects'][obj] # {'ocel:type': log2['ocel:objects'][obj]['ocel:type'], 'ocel:ovmap': log2['ocel:objects'][obj]['ocel:ovmap'] }
                            
    # validation
    ocel_lib.export_log(newLog, 'oceltest.json')
    if not ocel_lib.validate('oceltest.json', 'schema.json'):
        print(newLog)
        raise Exception("INVALID OCEL DOES NOT MATCH SCHEMA")
        
    print("successful validation of new log")
    
    return newLog




# interleaved miner section start ----------------------------------------------------------------------
def sortByTimeStamp(element):
    return element[2]["ocel:timestamp"]


# calculates interleaved event relation of two logs, used as helper for interleaved miner
def interleavedRelation(log1, log2, obj1, obj2):
    # calculate path from obj1 and obj2
    path = []
    for ev_id, event in log1["ocel:events"].items():
        if obj1 in event["ocel:omap"]:
            path.append((1, ev_id, event))
    
    for ev_id, event in log2["ocel:events"].items():
        if obj2 in event["ocel:omap"]:
            path.append((2, ev_id, event))
    
    path.sort(reverse=False, key=sortByTimeStamp)
    
    matchingEvents = set()
    
    for i in range(len(path)-1):
        if path[i][0] != path[i+1][0]:
            matchingEvents.add((path[i][:2], path[i+1][:2]))
    
    # returns set of relation tuples. Each tuple contains two tuples, 
    # first element of inner tuple indicates which log, second element indicates event id
    return matchingEvents


# calculates non interleaved event relation of two logs, used as helper for non/interleaved miner
def nonInterleavedRelation(log1, log2, obj1, obj2):
    # calculate path from obj1 and obj2
    path = []
    for ev_id, event in log1["ocel:events"].items():
        if obj1 in event["ocel:omap"]:
            path.append((1, ev_id, event))
    
    for ev_id, event in log2["ocel:events"].items():
        if obj2 in event["ocel:omap"]:
            path.append((2, ev_id, event))
    
    path.sort(reverse=False, key=sortByTimeStamp)
    
    matchingEvents = set()
    
    for i in range(len(path)-1):
        if path[i][0] != path[i+1][0]:
            if i+2 == len(path) or path[i+1][0] == path[i+2][0]:
                matchingEvents.add((path[i][:2], path[i+1][:2]))
    
    # returns set of relation tuples. Each tuple contains two tuples, 
    # first element of inner tuple indicates which log, second element indicates event id
    return matchingEvents


# interleaved and non-interleaved miner, depending on interleavedMode flag value
def interLeavedMiner(log1, log2, object_relationship, interleavedMode=True):
    # start with log1 since we want all its events and objects
    newLog = copy.deepcopy(log1)
    
    # adjust global
    newLog['ocel:global-log']['ocel:attribute-names'] = list(set(newLog['ocel:global-log']['ocel:attribute-names']).union(set(log2['ocel:global-log']['ocel:attribute-names'])))
    newLog['ocel:global-log']['ocel:object-types'] = list(set(newLog['ocel:global-log']['ocel:object-types']).union(set(log2['ocel:global-log']['ocel:object-types'])))

    newObjEventPairs = set()
    
    log1_objects = log1["ocel:objects"].keys()
    log2_objects = log2["ocel:objects"].keys()
    
    # restrict object relationship to objects in the logs
    crt_prd = [(x,y) for x in log1_objects for y in log2_objects]
    reduced_object_relationship = set(crt_prd).intersection(object_relationship)
    
    interleavedDict = {}
    for relation in reduced_object_relationship:
        if interleavedMode:
            interleavedDict[relation] = interleavedRelation(log1, log2, relation[0], relation[1])
        else:
            interleavedDict[relation] = nonInterleavedRelation(log1, log2, relation[0], relation[1])

    
    for ev_id1, event1 in log1["ocel:events"].items():
        for obj1 in event1["ocel:omap"]:
            for relation in reduced_object_relationship:
                if relation[0] == obj1:
                    obj2 = relation[1]
                    for ev_id2, event2 in log2["ocel:events"].items():
                        if obj2 in event2["ocel:omap"]:
                            if ((1, ev_id1), (2, ev_id2)) in interleavedDict[(obj1, obj2)]:
                                newObjEventPairs.add((ev_id1, obj2, ev_id2))

    # add new pairs to newLog
    for pair in newObjEventPairs:
        ev_id = pair[0]
        obj = pair[1]
        ev_id2 = pair[2]
        
        # add new object to event omap, but avoid duplicates
        objects = newLog["ocel:events"][ev_id]["ocel:omap"]
        objects.append(obj)
        newLog["ocel:events"][ev_id]["ocel:omap"] = list(set(objects))
        
        # fix vmap
        for key, value in log2["ocel:events"][ev_id2]["ocel:vmap"].items():
            if key not in newLog['ocel:events'][ev_id]['ocel:vmap']:
                newLog['ocel:events'][ev_id]['ocel:vmap'][key] = value

        # add new object to objects of log
        if obj not in newLog["ocel:objects"].keys():
            newLog["ocel:objects"][obj] = log2["ocel:objects"][obj]
    
    return newLog




# filter operator section start ----------------------------------------------------------------------

def removeEventsAndObjects(log, removeEvents):
    # remove events
    for ev_id in removeEvents:
        del log["ocel:events"][ev_id]

    # remove objects that aren't mentioned anymore
    remainingObjects = set()
    for ev_id, event in log["ocel:events"].items():
        for obj_id in event["ocel:omap"]:
            remainingObjects.add(obj_id)
    removeObjects = set(log["ocel:objects"].keys()).difference(remainingObjects)
    for obj_id in removeObjects:
        del log["ocel:objects"][obj_id]



# activities: set of activities
# filter out events that aren't in activities parameter set
def filterByActivity(log, activities):
    newLog = copy.deepcopy(log)
    
    # remove events that don't contain one of desired activity
    removeEvents = set()
    for ev_id, event in log["ocel:events"].items():
        if event["ocel:activity"] not in activities:
            removeEvents.add(ev_id)
    
    removeEventsAndObjects(newLog, removeEvents)
    
    return newLog


# attributes parameter: dictionary with attribute name and set of acceptable values
# events have to match all passed attributes
def filterByAttribute(log, attributes):
    newLog = copy.deepcopy(log)
    
    # remove events that don't contain desired attribute values
    removeEvents = set()
    for ev_id, event in log["ocel:events"].items():
        for attr in attributes.keys():
            if attr not in event["ocel:vmap"].keys():
                removeEvents.add(ev_id)
            else:
                if str(event["ocel:vmap"][attr]) not in attributes[attr]:
                    removeEvents.add(ev_id)

    removeEventsAndObjects(newLog, removeEvents)
    
    return newLog


# objects parameters: set of objects that we want to keep
def filterByObject(log, objects):
    newLog = copy.deepcopy(log)
    
    # find object types
    object_types = set()
    for obj in objects:
        if obj in log["ocel:objects"]:
            object_types.add(log["ocel:objects"][obj]["ocel:type"])

    # adjust global
    newLog['ocel:global-log']['ocel:object-types'] = list(object_types)

    # remove events that don't contain desired attribute values
    for ev_id, event in log["ocel:events"].items():
        intersec = objects.intersection(event["ocel:omap"])
        if intersec == set():
            del newLog["ocel:events"][ev_id]
        # remove other objects
        else:
            newLog["ocel:events"][ev_id]["ocel:omap"] = list(intersec)
    
    for obj_id in log["ocel:objects"]:
        if obj_id not in objects:
            del newLog["ocel:objects"][obj_id]
    
    return newLog


# timestamps parameter: (start_datetime, end_datetime)
def filterByTimestamp(log, timestamps):
    newLog = copy.deepcopy(log)
    
    start_datetime = timestamps[0]
    end_datetime = timestamps[1]
    
    # remove events that don't contain desired attribute values
    removeEvents = set()
    for ev_id, event in log["ocel:events"].items():
        date = event["ocel:timestamp"]
        if type(date) != datetime.datetime:
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        if not (start_datetime <= date and date <= end_datetime):
            removeEvents.add(ev_id)
            
    removeEventsAndObjects(newLog, removeEvents)
    
    return newLog


# filter modes:
#    activity, attribute, object, timestamp
# parameters:
#    actual filter criteria
def filterLog(log, parameters, mode="activity"):
    if mode == "activity":
        return filterByActivity(log, parameters)
    elif mode == "attribute":
        return filterByAttribute(log, parameters)
    elif mode == "object":
        return filterByObject(log, parameters)
    elif mode == "timestamp":
        return filterByTimestamp(log, parameters)