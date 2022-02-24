from halp.undirected_hypergraph import UndirectedHypergraph
from newHypergraphFunctions import *

L = read_edge_data("comorb_hypergraph_no_dups.txt")

myHypergraph = hypergraph(L)     # construct a hypergraph from the data

outputfile = "randomgraph.txt"
# construct an ER-like random hypergraph
ERlikeRandom = randomHypergraph(myHypergraph)
edgeList = ERlikeRandom.C
with open(outputfile, 'wb') as wfd:
    for i in range(len(edgeList)):
        myList = edgeList[i]
        myList = [str(int) for int in myList]
        wfd.write(','.join(myList).encode())
        wfd.write(('\n').encode())

    wfd.close()


# compute degree
#smalllHypergraphDegree = smalllHypergraph.D
# compute local clustering (this can be slow for large graphs)
#smallHypergraphLocalClustering= localClusteringHypergraph(smalllHypergraph)





