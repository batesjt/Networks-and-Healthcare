import json

import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
#import networkx as nx
#import hypernetx as hnx
import csv
import collections
import pickle
import os
##Currently DON'T DEAL WITH UNKOWNS/UNOBTAINABLE/NOT SPECIFIED
dataLocation = os.path.join("Datasets", 'demographic_comrb_primary_secondary_code.csv')
dataset = pd.read_csv(dataLocation)
dataset = dataset.drop_duplicates(["subject_id"])
ethnicites = np.array(dataset.drop_duplicates(["ethnicity_grouped"])["ethnicity_grouped"])
religions = np.array(dataset.drop_duplicates(["religion"])["religion"])
print(ethnicites)
# must include comorbidities
numComorbidities = 30
numEthnicities = len(ethnicites)
numReligions = len(religions)
numGenders = 2
numAgeGroups = 5
numNodes = numGenders + numAgeGroups + numComorbidities + numEthnicities + numReligions

# offsets for enumerating different types of nodes
genderNodeStart = numComorbidities
ageNodeStart = genderNodeStart + numGenders
ethnicityNodeStart = ageNodeStart + numAgeGroups
religionNodeStart = ethnicityNodeStart + numEthnicities

# rename comorbidities to nodes
comorbs = []
for i in range(numComorbidities):
    comorbs.append(str(i))

columns = ['hadm_id', 'subject_id', 'gender', 'age', 'ethnicity',
           'ethnicity_grouped', 'religion', 'primary_diagnosis', 'icd9_code',
           'icd9_4_digits'] + comorbs


def genderToNode(char):
    if (numGenders == 2):
        if char == "M":
            return str(genderNodeStart)
        if char == "F":
            return str(genderNodeStart + 1)
        else:
            raise ValueError
    else:
        return char


def ageToNode(int):
    if (numAgeGroups == 0):
        return int

    if (16 <= int < 25):
        return ageNodeStart

    if (25 <= int < 45):
        return (ageNodeStart + 1)

    if (45 <= int < 65):
        return (ageNodeStart + 2)

    if (65 <= int < 85):
        return (ageNodeStart + 3)

    if (int >= 85):
        return (ageNodeStart + 4)


def ethnicityToNode(string):
    if (numEthnicities == 0):
        return string
    nums = np.empty(numEthnicities)
    for i in range(numEthnicities):
        nums[i] = ethnicityNodeStart + i
    ethnicityDict = dict(zip(ethnicites, nums))
    return int(ethnicityDict.get(string))


def religionToNode(string):
    if (numReligions == 0):
        return string
    nums = np.empty(numReligions)
    for i in range(numReligions):
        nums[i] = religionNodeStart + i
    religionDict = dict(zip(religions, nums))
    return int(religionDict.get(string))


def countGenderNodesDegrees():
    genderNodesDegrees = np.ones(numGenders)
    genderNodesDegrees[0] = dataset[dataset["gender"] == str(genderNodeStart)]["gender"].count()
    genderNodesDegrees[1] = dataset[dataset["gender"] == str(genderNodeStart + 1)]["gender"].count()
    return genderNodesDegrees


def countAgeNodesDegrees():
    ageNodesDegrees = np.ones(numAgeGroups)
    for i in range(numAgeGroups):
        ageNodesDegrees[i] = dataset[dataset["age"] == (ageNodeStart + i)]["gender"].count()
    return ageNodesDegrees


def countEthnicityNodesDegrees():
    ethnicityNodeDegrees = np.ones(numEthnicities)
    for i in range(numEthnicities):
        ethnicityNodeDegrees[i] = dataset[dataset["ethnicity_grouped"] ==
                                          (ethnicityNodeStart + i)]["gender"].count()
    return ethnicityNodeDegrees


def countReligionNodesDegrees():
    religionNodeDegrees = np.ones(numReligions)
    for i in range(numReligions):
        religionNodeDegrees[i] = int(dataset[dataset["religion"]
                                             == (religionNodeStart + i)]["gender"].count())
    return religionNodeDegrees


def countComorbiditesDegrees():
    comorbiditiesNodeDegrees = np.ones(numComorbidities)
    for i in range(numComorbidities):
        comorbiditiesNodeDegrees[i] = dataset[dataset[str(i)]
                                              == i]["gender"].count()
    return comorbiditiesNodeDegrees


def getNodeDegrees():
    return np.concatenate([countComorbiditesDegrees()])#, countGenderNodesDegrees(), countAgeNodesDegrees()
                              #, countEthnicityNodesDegrees()])


# convert demographics to appropriate nodes
dataset.columns = columns
dataset["gender"] = dataset["gender"].apply(lambda x: genderToNode(x))
dataset["ethnicity_grouped"] = dataset["ethnicity_grouped"].apply(lambda x: ethnicityToNode(x))
dataset["religion"] = dataset["religion"].apply(lambda x: religionToNode(x))
dataset["age"] = dataset["age"].apply(lambda x: ageToNode(x))
for i in range(0, 30):
    dataset[str(i)] = dataset[str(i)].apply(lambda x: i if (x == 1) else -1)

outputfile = "only_comorbs_hypergraph.txt"

# edit if need to remove rows
# set initial degree count to number of demographics used
hyperedgeDegrees = np.empty(dataset["age"].count())

# edit list of dataset.iloc[i, _] to include only required demographics
# 2 - gender
# 3 - age
# 5 - ethnicity
# 6 - religion
def generateGraph():
    myDict = {}
    degreeCount = 0
    for i in range(len(dataset["age"])):
        myList = []
        #myList = [str(dataset.iloc[i, 2]), str(dataset.iloc[i, 5]), str(dataset.iloc[i, 3])]
        for j in range(10, 40):
            value = int(dataset.iloc[i, j])
            if (value != -1):
                myList.append(str(value))
                degreeCount += 1
        hyperedgeDegrees[i] = degreeCount
        degreeCount = 0
        myDict[i] = myList
    myDict = collections.OrderedDict(sorted(myDict.items()))
    with open("comorbsOnlygraphDict.pickle", "wb") as output_file:
        pickle.dump(myDict, output_file)
    print("graph generated")
    return myDict


def random_graph_gen(nodeDegreesArray, hyperedgeDegreesArray):
    print("generating random")
    outputDict = {}
    nodeCount = len(nodeDegreesArray)
    # edges = open(outputfile, "r")
    inputedges = np.arange(len(hyperedgeDegreesArray))
    nodes = np.arange(nodeCount)
    nodeDegreeSum = np.sum(nodeDegreesArray)
    hyperedgeDegreeSum = np.sum(hyperedgeDegreesArray)
    nodeProbability = np.array(list(map((lambda x: x / nodeDegreeSum), nodeDegreesArray)))
    hyperedgeProbability = np.array(list(map((lambda x: x / hyperedgeDegreeSum), hyperedgeDegreesArray)))
    outputNodes = np.empty(nodeCount)
    for i in range(int(nodeDegreeSum)):
        node = np.random.choice(nodes, 1, p=nodeProbability)
        edge = np.random.choice(inputedges, 1, p=hyperedgeProbability)[0]
        if node[0] not in outputDict.get(edge, []):
            outputDict[edge] = outputDict.get(edge, []) + [node[0]]

    myDictOrdered = {k: sorted(v) for k, v in outputDict.items()}
    myDictOrdered1 = collections.OrderedDict(sorted(myDictOrdered.items()))
    return myDictOrdered1

def saveDictAsTxt(randFile, randDict):
    print("saving file as: " + randFile)
    sortDict = collections.OrderedDict(sorted(randDict.items()))
    with open(randFile, "w") as f:
        for value in sortDict.values():
            #f.write(str((value[0])))
            for elem in value:
                f.write(str(elem))
                if elem != value[-1]:
                    f.write(",")
            f.write(('\n'))
    print("File saved!")

def negativeSampling(graphDict):
    print("Negative sampling graph")
    nodeDegreesArray = getNodeDegrees()
    nodes = np.arange(len(nodeDegreesArray))
    nodeDegreePowerSum = np.sum(list(map((lambda x: x ** (3 / 4)), nodeDegreesArray)))
    nodeProbability = np.array(list(map((lambda x: x ** (3/4) / nodeDegreePowerSum), nodeDegreesArray)))
    sampledGraphDict1 = removeSmallEdges(graphDict)
    #sampledGraphDict = {k:sorted(list(map((lambda x : int(x)), v)), key = int) for k, v in sampledGraphDict1.items()}
    sampledGraphDict = {k: sorted(v) for k, v in sampledGraphDict1.items()}
    #sampledGraphDict = removeSmallEdges(sampledGraphDict1)
    print("size:" + str(len(sampledGraphDict)))
    index = len(sampledGraphDict)
    for j in range(index):
        negEdge = sampledGraphDict.get(j)
        while (negEdge in sampledGraphDict.values()):
            alpha = np.random.uniform((1/3), 1)
            numReplace =  round(alpha * len(negEdge))
            #print("NumReplace:" + str(numReplace))
            for i in range(numReplace):
                node = negEdge[i]
                while (node in negEdge):
                    node = np.random.choice(nodes, 1, p=nodeProbability)
                negEdge[i] = int(node)
            negEdge = sorted(negEdge)
        sampledGraphDict[index] = negEdge
        index += 1
    print("Negative Sampling finished.")
    return sampledGraphDict

def removeSmallEdges(inputDictGraph):
    temp = []
    res = dict()
    count=0
    for key, val in inputDictGraph.items():
        if len(val) > 2:
            temp.append(val)
            res[count] = val
            count+=1
    return res

def removeDuplicateEdges(inputDictGraph):
    temp = []
    res = dict()
    count=0
    for key, val in inputDictGraph.items():
        if val not in temp:
            if val != []:
                temp.append(val)
                res[count] = val
                count+=1
    return res

#graphDict1 = removeDuplicateEdges(generateGraph())



#graphFile= open('comorbsOnlygraphDict.pickle', 'rb')
#graphDict = pickle.load(graphFile)
#trainingDict = collections.OrderedDict(list(sorted(graphDict1.items()))[5000:7000])
#print(trainingDict[5000])
# print(sorted(trainingDict.keys()))
# flat_list = set([item for sublist in trainingDict.values() for item in sublist])
# print(sorted(flat_list, key=int))
#sampledDict = negativeSampling(trainingDict)
#print(sampledDict[0])
#saveDictAsTxt("testGraph(ComorbsOnly).txt", sampledDict)
