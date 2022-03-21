import main_approx_ver2_wip as mochy
import main_adv as rg
import main_exact as me
import pickle
input = "dblp_graph.txt"
#car = mochy.h_motifs_count(input)
a = me.h_motifs_count_individual(input)
print("nice one")
print(len(a))
with open("features.pickle", "wb") as output_file:
    pickle.dump(len(a), output_file)



# dump information to that file
data = pickle.load(file)

# close the file
file.close()
print(data)