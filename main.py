import random

from numpy.f2py.crackfortran import postcrack


def calculate_weights(nodes, edges):

    weights = []

    for i in range(position):
        new_weight = nodes[i][0]
        for j in range(i, position):
            new_weight += edges[j]
        weights.append(new_weight)

    for i in range(position,len(nodes)):
        new_weight = nodes[i][0]
        for j in range(position,i):
            new_weight += edges[j]
        weights.append(new_weight)

    return weights

def step(nodes, edges):

    nodes[position][1] = 1
    for j in range(0, len(nodes)):
        nodes[j][0] -= edges[position-1]
        if nodes[j][0] < 0 and nodes[j][1] != 1:
            print(f"Node {j} was not reached before the requested time.")
            print(nodes)
            exit()
    return nodes

def new_target(nodes):
    targets = [x for x in total_weights if nodes[total_weights.index(x)][1] == 0]
    print(targets)
    if targets == []:
        return -1
    target = total_weights.index(min(targets))
    return target

#main

nodes = []
edges = []
total_weights = []
size = 10
position =  random.randint(0, size-1)
target = 0
ALL_VISITED = False

for i in range(size):
    nodes.append([random.randint(230, 250),0])
    edges.append(random.randint(1, 5))

nodes[position][1] = 1
total_weights = calculate_weights(nodes, edges)
print(nodes)
print(total_weights)

target = new_target(nodes)

while target != -1:
    print(f"Current position: {position}")
    print(f"Current target: {target}")
    if position > target:
        while position >= target:
            nodes = step(nodes,edges)
            total_weights = calculate_weights(nodes, edges)
            position -= 1
        position += 1
    else:
        while position <= target:
            nodes = step(nodes,edges)
            total_weights = calculate_weights(nodes, edges)
            position += 1
        position -=1
    target = new_target(nodes)
    print(nodes)
