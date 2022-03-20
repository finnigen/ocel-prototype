import copy
import json
import ocel as ocel_lib



# input: 2 ocels, object relationship, attribute name(s) from ocels
# output: 1 ocel, objects from log2 merged into log1 based on matches in values of passed attribute(s)
# attribute 1 are attribute names from log1, while attribute2 are attribute names from log2
def matchMiner(log1, log2, object_relation, attribute1, attribute2=""):
    if attribute2 == "":
        attribute2 = attribute1
    # start from log1 since we want to merge objects from log2 into log1
    newLog = copy.deepcopy(log1)
    
    # adjust global
    newLog['ocel:global-log']['ocel:attribute-names'] = list(set(newLog['ocel:global-log']['ocel:attribute-names']).union(set(log1['ocel:global-log']['ocel:attribute-names'])))
    newLog['ocel:global-log']['ocel:object-types'] = list(set(newLog['ocel:global-log']['ocel:object-types']).union(set(log1['ocel:global-log']['ocel:object-types'])))

    added_objects = set()
    # find objects in log2 that match attribute value and are in object relation
    # adjust events
    for i in range(len(newLog['ocel:events'])):
        for j in range(len(log2['ocel:events'])):
            if attribute1 in log1['ocel:events'][str(i)]['ocel:vmap'].keys() and attribute2 in log2['ocel:events'][str(i)]['ocel:vmap'].keys():
                if log1['ocel:events'][str(i)]['ocel:vmap'][attribute1] == log2['ocel:events'][str(j)]['ocel:vmap'][attribute2]:
                    for obj1 in newLog['ocel:events'][str(i)]['ocel:omap']:
                        for obj2 in log2['ocel:events'][str(j)]['ocel:omap']:
                            if (obj1, obj2) in object_relation: ####### THIS HAS TO BE ADJUSTED DEPENDING ON FORMAT OF object_relation or format adjusted
                                added_objects.add(obj2)
                                newLog['ocel:events'][str(i)]['ocel:omap'] = list(set(newLog['ocel:events'][str(i)]['ocel:omap']).union([obj2]))
        
    # adjust objects
    for obj in added_objects:
        newLog['ocel:objects'][obj] = {'ocel:type': log2['ocel:objects'][obj]['ocel:type'],
                                       'ocel:ovmap': log2['ocel:objects'][obj]['ocel:ovmap'] }
                            
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
    newLog['ocel:global-log']['ocel:attribute-names'] = list(set(newLog['ocel:global-log']['ocel:attribute-names']).union(set(log1['ocel:global-log']['ocel:attribute-names'])))
    newLog['ocel:global-log']['ocel:object-types'] = list(set(newLog['ocel:global-log']['ocel:object-types']).union(set(log1['ocel:global-log']['ocel:object-types'])))
    
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
    
    # adjust objects
    for obj in added_objects:
        newLog['ocel:objects'][obj] = {'ocel:type': log2['ocel:objects'][obj]['ocel:type'],
                                       'ocel:ovmap': log2['ocel:objects'][obj]['ocel:ovmap'] }
                            
    # validation
    ocel_lib.export_log(newLog, 'oceltest.json')
    if not ocel_lib.validate('oceltest.json', 'schema.json'):
        print(newLog)
        raise Exception("INVALID OCEL DOES NOT MATCH SCHEMA")
        
    print("successful validation of new log")
    
    return newLog