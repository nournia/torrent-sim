import matplotlib.pyplot as plt
import networkx as nx

peer_count = 10

# read results
res = open('result.txt')
edges = {}
for line in res:
	edge = tuple([int(x[4:]) for x in line.split()])
	if edge in edges:
		edges[edge] += 1
	else:
		edges[edge] = 1

links = []
counts = []
for i in range(peer_count):
	for j in range(i+1, peer_count):
		links.append((i, j))
		count = 0
		if (i, j) in edges: count += edges[i, j]
		if (j, i) in edges: count += edges[j, i]
		counts.append(count)

# show results in graph
G = nx.Graph()
G.add_nodes_from(range(peer_count))
colors = counts
G.add_edges_from(links)

nx.draw_circular(G, node_color='#A0CBE2', edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=False)
plt.show()
