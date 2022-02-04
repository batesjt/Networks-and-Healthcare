from halp.undirected_hypergraph import UndirectedHypergraph
from newHypergraphFunctions import *

L = read_edge_data("comorb_graph_sample")

smalllHypergraph = hypergraph(L)     # construct a hypergraph from the data


# construct an ER-like random hypergraph
ERlikeRandomHypergraphSmall = randomHypergraph(smalllHypergraph)

# compute degree
smalllHypergraphDegree = smalllHypergraph.D
# compute local clustering (this can be slow for large graphs)
smallHypergraphLocalClustering= localClusteringHypergraph(smalllHypergraph)





