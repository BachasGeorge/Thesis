import random

nodes = []
edges = []
total_weights = []

nodes.append([random.randint(120, 150), 0])
total_weights.append(nodes[0])

for i in range(1, 100):
    nodes.append([random.randint(120, 150), 0])
    edges.append(random.randint(1, 5))
    weight = nodes[i][0]
    for j in range(0,i):
        weight += edges[j]
    total_weights.append([weight, i])

sorted_weights = sorted(total_weights, reverse=True, key=lambda x: x[0])
