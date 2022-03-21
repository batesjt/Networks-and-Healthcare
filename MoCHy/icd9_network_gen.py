import itertools

import pandas as pd
#import matplotlib.pyplot as plt
#import networkx as nx
#import hypernetx as hnx
import csv
import collections
import pickle
import numpy as np
import comorb_hgraph_generator as chg
from collections import Counter
import os
dataLocation = os.path.join("Datasets", 'mimic_iii_icu_admission_dataframe_with_diagnoses_over_16_dummies.csv')
dataset = pd.read_csv(dataLocation)
#print(flatlist)
#print(flat_list)
#print(unique_list)
#print(type(dataset['secondary_icd9'][0]))

dataset['16-24'] = dataset['16-24'].apply(lambda x: 0 if (x == 1) else -1)
dataset['25-44'] = dataset['25-44'].apply(lambda x: 1 if (x == 1) else -1)
dataset['45-64'] = dataset['45-64'].apply(lambda x: 2 if (x == 1) else -1)
dataset['65-84'] = dataset['65-84'].apply(lambda x: 3 if (x == 1) else -1)
dataset['over85'] = dataset['over85'].apply(lambda x: 4 if (x == 1) else -1)
dataset['M'] = dataset['M'].apply(lambda x: 5 if (x == 1) else -1)
dataset['F'] = dataset['F'].apply(lambda x: 6 if (x == 1) else -1)
icd9_merged = dataset['primary_icd9'] + ',' + dataset['secondary_icd9']
icd9 = icd9_merged.apply(lambda x : x.split(",")).tolist()
flat_list = [item for sublist in icd9 for item in sublist]
#print(Counter(flat_list)[:20])
#nodeDegrees = dict(itertools.islice(Counter(flat_list).items(), 20))
nodeDegreesDict = collections.OrderedDict(sorted(Counter(flat_list).items()))
with open("nodeDegreesDict.pickle", "wb") as output_file:
    pickle.dump(nodeDegreesDict, output_file)
nodesNamed = list(nodeDegreesDict.keys())
#print("names of nodes:")
#print(nodesNamed)
nodeDegrees = list(nodeDegreesDict.values())
#print(nodeDegrees)[:50]
print(len(nodeDegreesDict.keys()))
#unique_list = sorted(list(set(flat_list)))
#print(len(unique_list))
#print(icd9[0])
hyperedgeDegrees = np.empty(dataset["age"].count())
def generateGraph():
    myDict = {}
    degreeCount = 0
    for i in range(len(icd9)):
        myList = [nodesNamed.index(x) for x in icd9[i]]
        if 6049 in myList:
            print("found 0")
            print(myList)
            print(i)
        #icd9[i].apply(lambda x : nodesNamed.index(x))
        #myList = []
        #myList = [str(dataset.iloc[i, 2]), str(dataset.iloc[i, 5]), str(dataset.iloc[i, 3])]
        #for j in range(10, 40):
            #value = int(dataset.iloc[i, j])
            #if (value != -1):
                #myList.append(str(value))
                #degreeCount += 1
        hyperedgeDegrees[i] = len(myList)
        #degreeCount = 0
        myDict[i] = myList

    myDictOrdered = {k: sorted(v) for k, v in myDict.items()}
    myDictOrdered1 = collections.OrderedDict(sorted(myDictOrdered.items()))
    print(list(myDictOrdered1.items())[0:5])
    with open("icd9OnlyDict.pickle", "wb") as output_file:
        pickle.dump(myDictOrdered1, output_file)
    print("graph generated")
    print(sum(hyperedgeDegrees))
    return myDictOrdered1


def negativeSampling(graphDict, icd9NodesDict):
    print("Negative sampling graph")
    nodeDegreesArray = list(icd9NodesDict.values())
    nodes = np.arange(len(icd9NodesDict))
    nodeDegreePowerSum = np.sum(list(map((lambda x: x ** (3 / 4)), nodeDegreesArray)))
    nodeProbability = np.array(list(map((lambda x: x ** (3/4) / nodeDegreePowerSum), nodeDegreesArray)))
    sampledGraphDict = chg.removeSmallEdges(graphDict)
    print(list(sampledGraphDict.items())[0])
    #sampledGraphDict = {k:sorted(list(map((lambda x : int(x)), v)), key = int) for k, v in sampledGraphDict1.items()}
    #sampledGraphDict = {k: sorted(v) for k, v in sampledGraphDict1.items()}
    #sampledGraphDict = removeSmallEdges(sampledGraphDict1)
    print("size:" + str(len(sampledGraphDict)))
    index = len(sampledGraphDict)
    for j in range(len(sampledGraphDict)):
        #print(list(sampledGraphDict.items())[0])
        negEdge = [i for i in sampledGraphDict.get(j)]
        while (negEdge in sampledGraphDict.values()):
            alpha = np.random.uniform((1/3), 1)
            numReplace =  round(alpha * len(negEdge))
            #print("NumReplace:" + str(numReplace))
            swapped = []
            for i in range(numReplace):
                x = -1
                while(x== -1 | x in swapped):
                    x = np.random.randint(low=0, high=(len(negEdge)-1))
                node = negEdge[x]
                swapped.append(x)
                while (node in negEdge):
                    node = np.random.choice(nodes, 1, p=nodeProbability)[0]
                negEdge[i] = node
            negEdge = sorted(negEdge)
            swapped = []
        sampledGraphDict[index] = negEdge
        #print(index)
            #print(j)
            #print(sampledGraphDict[index])
            #print(sampledGraphDict.get(0))
            #print(list(sampledGraphDict.items())[j])
            #print(list(sampledGraphDict.items())[0])
            #print(sampledGraphDict[j])

        index += 1
    print("Negative Sampling finished.")
    myDictOrdered1 = collections.OrderedDict(sorted(sampledGraphDict.items()))
    return myDictOrdered1
outputDict = generateGraph()
#chg.saveDictAsTxt("icd9Only.txt", outputDict)

#graphFile= open('icd9OnlyDict.pickle', 'rb')
#graphDict = pickle.load(graphFile)
sampledDict = negativeSampling(outputDict,nodeDegreesDict)
#print(sampledDict[0])
chg.saveDictAsTxt("sampledICD9Only.txt", sampledDict)