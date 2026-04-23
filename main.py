import random

def calculate_weights(nodes, edges, position):

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


def step(nodes, edges, position, direction):

    edge_cost = edges[position] if direction == 1 else edges[position - 1]
    new_position = position + direction
    for i in range(0, len(nodes)):
        if nodes[i][1] == 0:
            nodes[i][0] -= edge_cost
            if nodes[i][0] < 0:
                print(f"Node {i} expired before it could be visited!")
                return nodes, new_position, True  # True = failure
    nodes[new_position][1] = 1
    return nodes, new_position, False

def move_towards(nodes, edges, position, target):
    direction = 1 if target > position else -1
    while position != target:
        nodes, position, failed = step(nodes, edges, position, direction)
        if failed:
            return nodes, position, True
    return nodes, position, False

def new_target():
    targets = [x for x in total_weights if nodes[total_weights.index(x)][1] == 0]
    if not targets:
        return -1
    target = total_weights.index(min(targets))
    return target

# ────── Setup ──────

SIZE = 50
nodes = [[random.randint(230, 250), 0] for _ in range(SIZE)]
edges = [random.randint(1, 5) for _ in range(SIZE-1)]

position =  random.randint(0, SIZE-1)
nodes[position][1] = 1

print(f"Starting at node {position}")
print(f"Initial nodes : {nodes}")
print(f"Edges         : {edges}")

# ────── Main ──────

total_weights = calculate_weights(nodes, edges, position)
target = new_target()

while target != -1:
    print(f"\nPosition: {position}  →  Target: {target}  "
          f"(effective weight: {total_weights[target]:.1f})")

    nodes, position, failed = move_towards(nodes, edges, position, target)
    if failed:
        print("Mission failed — a node expired.")
        break

    total_weights = calculate_weights(nodes, edges, position)
    target = new_target()
    print(f"Nodes: {nodes}")
else:
    print("\nAll nodes were visited successfully!")