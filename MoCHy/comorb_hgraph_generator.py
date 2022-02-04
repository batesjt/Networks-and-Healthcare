import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import hypernetx as hnx

##Currently DON'T DEAL WITH UNKOWNS/UNOBTAINABLE/NOT SPECIFIED
dataset = pd.read_csv('demographic_comrb_primary_secondary_code.csv')
dataset = dataset.drop_duplicates(["subject_id"])
ethnicites = np.array(dataset.drop_duplicates(["ethnicity_grouped"])["ethnicity_grouped"])
religions = np.array(dataset.drop_duplicates(["religion"])["religion"])

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
    return np.concatenate([countComorbiditesDegrees(), countGenderNodesDegrees(), countAgeNodesDegrees()
                              , countEthnicityNodesDegrees(), countReligionNodesDegrees()])


# convert demographics to appropriate nodes
dataset.columns = columns
dataset["gender"] = dataset["gender"].apply(lambda x: genderToNode(x))
dataset["ethnicity_grouped"] = dataset["ethnicity_grouped"].apply(lambda x: ethnicityToNode(x))
dataset["religion"] = dataset["religion"].apply(lambda x: religionToNode(x))
dataset["age"] = dataset["age"].apply(lambda x: ageToNode(x))
for i in range(0, 29):
    dataset[str(i)] = dataset[str(i)].apply(lambda x: i if (x == 1) else -1)

outputfile = "comorb_hypergraph_no_dups.txt"

# edit if need to remove rows
# set initial degree count to number of demographics used
hyperedgeDegrees = np.empty(dataset["age"].count())
degreeCount = 3

# edit list of dataset.iloc[i, _] to include only required demographics
# 2 - gender
# 3 - age
# 5 - ethnicity
# 6 - religion

myDict = {}
#editted to halp format
with open(outputfile, 'wb') as wfd:
    for i in range(dataset["age"].count()):
        #myList = [str(dataset.iloc[i, 2]), str(dataset.iloc[i, 5]), str(dataset.iloc[i, 3])]
        wfd.write((dataset.iloc[i, 2] + ',' +
                    str(dataset.iloc[i, 5]) + ',' +
                    str(dataset.iloc[i, 3])
                    ).encode())

        for j in range(10, 39):
            value = int(dataset.iloc[i, j])
            if (value != -1):
                #myList.append(str(value))
                wfd.write(("," + str(value)).encode())
                degreeCount += 1
        wfd.write(('\n').encode())
        #wfd.write((' 1' + "\n").encode())
        hyperedgeDegrees[i] = degreeCount
        degreeCount = 3
        #myDict[i] = myList
    wfd.close()
#H = hnx.Hypergraph(myDict)
#hnx.draw(H)

##################
def random_graph_gen(nodeDegreesArray, hyperedgeDegreesArray):
    nodeCount = len(nodeDegreesArray)
    edges = open(outputfile, "r")
    output = open("random_hypergraph.txt", "w")
    inputedges = np.arange(len(hyperedgeDegreesArray))
    nodes = np.arange(nodeCount)
    nodeDegreeSum = np.sum(nodeDegreesArray)
    hyperedgeDegreeSum = np.sum(hyperedgeDegreesArray)
    nodeProbability = np.array(list(map((lambda x: x / nodeDegreeSum), nodeDegreesArray)))
    print(nodeProbability.sum())
    hyperedgeProbability = np.array(list(map((lambda x: x / hyperedgeDegreeSum), hyperedgeDegreesArray)))
    outputNodes = np.empty(nodeCount)
    for i in range(int(nodeDegreeSum)):
        node = np.random.choice(nodes, 1, p=nodeProbability)
        edge = edges.readline(np.random.choice(inputedges, 1, p=hyperedgeProbability)[0])
        output.write(edge.strip() + ", " + str(node[0]) + "\n")

    edges.close()
    output.close()


#random_graph_gen(getNodeDegrees(), hyperedgeDegrees)
