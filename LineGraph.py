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
                return nodes, new_position, True, i  # True = failure
    nodes[new_position][1] = 1
    return nodes, new_position, False, -1

# First steps when I was just picking the smallest node, maybe I'll need it later.
"""
def get_target(nodes, edges, position):
    weights = calculate_weights(nodes, edges, position)
    unvisited = [(weights[i], i) for i in range(len(nodes)) if nodes[i][1] == 0]
    if not unvisited:
        return -1
    selected = min(unvisited)[1]
    if position != 0 and position != len(nodes)-1:
        if selected <= (len(nodes)-1)/2 <= position:
            cost_to_reach_side = sum(edges[position:len(edges)-1])
            if min(unvisited)[0] - 2*cost_to_reach_side >= 0:
                selected = len(nodes)-1
        if selected >= (len(nodes)-1)/2 >= position:
            cost_to_reach_side = sum(edges[0:position-1])
            if min(unvisited)[0] - 2*cost_to_reach_side >= 0:
                selected = 0
    print(f"New target: {selected}")
    return selected
"""

# ────── Route planning ──────

def expires(nodes, edges, position, to):
    """
    Simulates the way we chose to traverse the graph and checks if a node expires this way.
    Returns the index of the node that expires or -1.
    """
    simulated_nodes = [n[:] for n in nodes] # make a copy of the list so the nodes visited in the simulation won't get marked
    direction = 1 if to > position else -1
    current = position
    while current != to:
        simulated_nodes, current, failed, i = step(simulated_nodes, edges, current, direction)
        if failed :
            return simulated_nodes, i
    return simulated_nodes, -1


def plan_route(nodes, edges, position):
    """
    Special cases:
      - Bot already at node 0   -> only one leg: 0 -> right_end
      - Bot already at right_end -> only one leg: right_end -> 0

    General case (bot somewhere in the middle):
      - Try nearer-end-first (optimal step count).
      - Simulate both legs; if any node would expire, print a warning (will solve this later)
      - Return whichever path is chosen

    Returns (sweep_targets)
      sweep_targets -- ordered list of end-nodes the bot must reach in turn
    """

    right_end = len(nodes) - 1

    # ── Already at an end: only one leg needed ──
    if position == 0:
        _, expired_node = expires(nodes, edges, position, right_end)
        if expired_node != -1 :
            print(f"!!!ATTENTION!!!\nNode {expired_node} will expire.\n!!!ATTENTION!!!")

    if position == right_end:
        _, expired_node = expires(nodes, edges, position, 0)
        if expired_node != -1 :
            print(f"!!!ATTENTION!!!\nNode {expired_node} will expire.\n!!!ATTENTION!!!")

    # ── General case: bot is in the middle ──
    dist_left = position  # steps to reach node 0
    dist_right = right_end - position  # steps to reach node right_end

    # Nearer end is the optimal first leg
    if dist_left < dist_right:
        near_end, far_end = 0, right_end
    else:
        near_end, far_end = right_end, 0

    simulated_nodes, expired_node = expires(nodes, edges, position, near_end)
    _, expired_node = expires(simulated_nodes, edges, near_end, far_end)
    if expired_node != -1:
        print(f"!!!ATTENTION!!!\nNode {expired_node} will expire.\n!!!ATTENTION!!!")

    return [near_end, far_end] # general

# ────── Simulation class ──────

class BotSimulation:
    """
    Call `.advance()` once per button press; it moves the bot exactly one
    node toward its current target and returns a status string.
    """

    def __init__(self, size=18, value_range=(80, 100), edge_range=(3, 5)):
        self.size = size
        self.nodes = [[random.randint(*value_range), 0] for _ in range(size)]
        self.edges = [random.randint(*edge_range) for _ in range(size - 1)]
        self.position = random.randint(0, size - 1)
        self.nodes[self.position][1] = 1


        # Plan the full route once and commit
        sweep_targets = plan_route(self.nodes, self.edges, self.position)
        # The bot visits near_end first, then far_end
        self.sweep_targets = sweep_targets
        self.target = self.sweep_targets[0]

        self.done = False
        self.failed = False
        self.step_count = 0
        self.last_from = -1        # previous position (for edge highlighting)
        self.expired_node = -1

        print(f"Starting at node {self.position}")
        print(f"Node values : {[n[0] for n in self.nodes]}")
        print(f"Edges       : {self.edges}")
        print(f"First target: {self.target}")

    def advance(self):

        # Move one step toward the current target.
        if self.done:
            return "Simulation already finished."

        direction = 1 if self.target > self.position else -1
        previous_position = self.position
        self.nodes, self.position, failed, expired = step(self.nodes, self.edges, self.position, direction)
        self.last_from = previous_position
        self.step_count += 1

        if failed:
            self.failed = True
            self.done = True
            self.expired_node = expired
            msg = f"Node {expired} expired — mission failed!"
            print(msg)
            return msg

        msg = f"Step {self.step_count}: moved {previous_position} → {self.position}  (target: {self.target})"
        print(msg)

        """
        # Arrived at target — pick next one
        if self.position == self.target:
            self.target = get_target(self.nodes, self.edges, self.position)
            if self.target == -1:
                self.done = True
                print("All nodes visited successfully!")
        """

        # Reached the end of the current sweep leg -- move to next leg if any
        if self.position == self.target:
            self.sweep_targets.pop(0)
            if self.sweep_targets:
                self.target = self.sweep_targets[0]
                self.is_detour = False  # second leg is always a plain sweep
                print(f"  Reached end. Now sweeping to {self.target}.")
            else:
                self.done = True
                print("All nodes visited successfully!")


        return msg

    @property
    def visited_count(self):
        return sum(1 for n in self.nodes if n[1] == 1)


# ────── CLI demo (runs when executed directly) ──────

if __name__ == "__main__":
    sim = BotSimulation(size=18)
    print("\nPress Enter to advance one step, or type 'q' to quit.\n")
    while not sim.done:
        user = input(f"[Step {sim.step_count}] Press Enter / q: ").strip().lower()
        if user == "q":
            break
        msg = sim.advance()
        print(f"  {msg}")
        print(f"  Visited: {sim.visited_count}/{sim.size}  |  "
              f"Position: {sim.position}  |  Next target: {sim.target}")
    if sim.done and not sim.failed:
        print("\nAll nodes visited successfully!")
