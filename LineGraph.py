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
                return nodes, new_position, True, i  # True = failure
    nodes[new_position][1] = 1
    return nodes, new_position, False, -1

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


# ────── Simulation class ──────

class BotSimulation:
    """
    Call `.advance()` once per button press; it moves the bot exactly one
    node toward its current target and returns a status string.
    """

    def __init__(self, size=20, value_range=(80, 150), edge_range=(1, 5)):
        self.size = size
        self.nodes = [[random.randint(*value_range), 0] for _ in range(size)]
        self.edges = [random.randint(*edge_range) for _ in range(size - 1)]
        self.position = random.randint(0, size - 1)
        self.nodes[self.position][1] = 1

        self.target = get_target(self.nodes, self.edges, self.position)
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

        if self.target == -1:
            self.done = True
            return "All nodes visited successfully!"

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

        # Arrived at target — pick next one
        if self.position == self.target:
            self.target = get_target(self.nodes, self.edges, self.position)
            if self.target == -1:
                self.done = True
                print("All nodes visited successfully!")

        return msg

    @property
    def visited_count(self):
        return sum(1 for n in self.nodes if n[1] == 1)


# ────── CLI demo (runs when executed directly) ──────

if __name__ == "__main__":
    sim = BotSimulation(size=20)
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
