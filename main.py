import random

def calculate_weights(nodes, edges):

    weights = []

    for i in range(len(nodes)):
        if i < position:
            travel_cost = sum(edges[i:position])  # edges between i and position
        elif i > position:
            travel_cost = sum(edges[position:i])  # edges between position and i
        else:
            travel_cost = 0  # current node
        weights.append(nodes[i][0] - travel_cost)
    return weights


def step(nodes, edges):

    for i in range(0, len(nodes)):
        if nodes[i][1] == 0:
            nodes[i][0] -= edges[position - 1]
            if nodes[i][0] < 0:
                print(f"Node {i} was not reached before the requested time.")
                print(nodes)
                exit()
    return nodes

def new_target():
    targets = [x for x in total_weights if nodes[total_weights.index(x)][1] == 0]
    print(targets)
    if not targets:
        return -1
    target = total_weights.index(min(targets))
    return target

#main

nodes = []
edges = []
total_weights = []
size = 50
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

target = new_target()

while target != -1:
    print(f"Current position: {position}")
    print(f"Current target: {target}")
    if position > target:
        while position >= target:
            nodes = step(nodes,edges)
            total_weights = calculate_weights(nodes, edges)
            position -= 1
            nodes[position][1] += 1
        position += 1
    else:
        while position <= target:
            nodes = step(nodes,edges)
            total_weights = calculate_weights(nodes, edges)
            position += 1
            nodes[position][1] += 1
        position -=1
    target = new_target()
    print(nodes)
print("All nodes were visited.")