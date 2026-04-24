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


# ────── Route planning ──────

def simulate_sweep(nodes, edges, position, first_end, second_end):
    """Simulate a full two-leg sweep on *copies* of the node weights.

    Leg 1: position -> first_end
    Leg 2: first_end -> second_end

    Returns a list of node indices that would expire (reach weight <= 0 before
    being visited) during this sweep, in the order they expire.
    The actual nodes/edges lists are never mutated.
    """
    weights = [n[0] for n in nodes]
    visited = [n[1] for n in nodes]
    visited[position] = 1

    would_expire = []

    def travel(frm, to):
        direction = 1 if to > frm else -1
        cur = frm
        while cur != to:
            edge_cost = edges[cur] if direction == 1 else edges[cur - 1]
            cur += direction
            for i in range(len(weights)):
                if not visited[i]:
                    weights[i] -= edge_cost
                    if weights[i] <= 0 and i not in would_expire:
                        would_expire.append(i)
            visited[cur] = 1

    travel(position, first_end)
    travel(first_end, second_end)
    return would_expire


def plan_route(nodes, edges, position):
    """Decide the committed sweep direction at the start of a run.

    Special cases:
      - Bot already at node 0   -> only one leg: 0 -> right_end
      - Bot already at right_end -> only one leg: right_end -> 0

    General case (bot somewhere in the middle):
      - Try nearer-end-first (optimal step count).
      - Simulate both legs; if any node would expire, warn and try the
        farther-end-first path instead.
      - Return whichever path is chosen, along with is_detour flag.

    Returns (sweep_targets, is_detour)
      sweep_targets -- ordered list of end-nodes the bot must reach in turn
      is_detour     -- True when we flipped to farther-end-first
    """
    right_end = len(nodes) - 1

    # ── Already at an end: only one leg needed ──
    if position == 0:
        expiries = simulate_sweep(nodes, edges, position, right_end, right_end)
        # single leg: 0 -> right_end (second_end == first_end means no 2nd leg)
        expiries = simulate_sweep(nodes, edges, position, right_end, right_end)
        if expiries:
            for node_idx in expiries:
                print(f"Node {node_idx} will expire before visiting the whole graph")
        return [right_end], False

    if position == right_end:
        expiries = simulate_sweep(nodes, edges, position, 0, 0)
        if expiries:
            for node_idx in expiries:
                print(f"Node {node_idx} will expire before visiting the whole graph")
        return [0], False

    # ── General case: bot is in the middle ──
    dist_left = position  # steps to reach node 0
    dist_right = right_end - position  # steps to reach node right_end

    # Nearer end is the optimal first leg
    if dist_left < dist_right:
        near_end, far_end = 0, right_end
    else:
        near_end, far_end = right_end, 0

    # Check nearer-end-first
    expiries = simulate_sweep(nodes, edges, position, near_end, far_end)
    if not expiries:
        return [near_end, far_end], False

    for node_idx in expiries:
        print(f"Node {node_idx} will expire before visiting the whole graph")

    # Fallback: farther-end-first
    expiries_alt = simulate_sweep(nodes, edges, position, far_end, near_end)
    if not expiries_alt:
        return [far_end, near_end], True

    for node_idx in expiries_alt:
        print(f"Node {node_idx} will expire before visiting the whole graph")

    return [far_end, near_end], True


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

        #self.target = get_target(self.nodes, self.edges, self.position)

        # Plan the full route once and commit
        sweep_targets, is_detour = plan_route(self.nodes, self.edges, self.position)
        # The bot visits near_end first, then far_end
        self.sweep_targets = sweep_targets
        self.target = self.sweep_targets[0]
        self.is_detour = is_detour

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

        """
        if self.target == -1:
            self.done = True
            return "All nodes visited successfully!"
        """

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
