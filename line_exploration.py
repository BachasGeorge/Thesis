"""

Core algorithm for single-robot line exploration with deadlines.

Feasibility / optimal-time case based on Algorithm 1 from:
  "Exploring Graphs with Time Constraints by Unreliable Collections of Mobile Robots"
  Czyzowicz, Godon, Kranakis, Labourel, Markou (SOFSEM 2018)

Best-effort case (what to do when not every deadline can be met) is our own
extension, following the *goal* set out for a different topology in:
  "Deadlines" — Das, Giachoudis, Luccio, Markou

"""

LEFT  = "left"
RIGHT = "right"


# ── data structures ────────────────────────────────────────────────────────────

class Node:
    """
    A node in the weighted line graph.

    Parameters
    ----------
    index        : position along the line (0-based)
    deadline     : latest time the robot may arrive here
    weight_right : travel time along the edge to node (index+1);
                   set to 0 for the last node
    """
    def __init__(self, index: int, deadline: float, weight_right: float = 0.0):
        self.index        = index
        self.deadline     = deadline
        self.weight_right = weight_right


class SnapNode:
    """
    One step of a reconstructed exploration path.

    Represents the state: "the robot has explored interval [i, j], is
    currently sitting at the left end (i) or right end (j), and has
    accumulated `count` on-time visits so far."

    Paper notation:
      side == LEFT   <->  (i-bar, j)
      side == RIGHT  <->  (i, j-bar)
    """
    def __init__(self, i: int, j: int, side: str, time: float, count: int, on_time: bool):
        self.i       = i
        self.j       = j
        self.side    = side    # LEFT or RIGHT
        self.time    = time    # arrival time at this snap node
        self.count   = count   # on-time visits accumulated so far (including this one)
        self.on_time = on_time # was THIS step's newly-explored node on time?

    @property
    def newly_explored(self) -> int:
        """Line-graph node that was first visited upon arrival at this snap node."""
        return self.i if self.side == LEFT else self.j


# ── main algorithm ─────────────────────────────────────────────────────────────

def explore(nodes: list, start: int):
    """
    Best-effort exploration of a line graph: finds the traversal that
    visits the largest possible number of nodes before their deadlines,
    and among those the one that finishes soonest. The walk stops as
    soon as nothing more can be gained, so expired nodes beyond the last
    useful node on either side are never visited.

    Parameters
    ----------
    nodes : ordered list of Node objects (index 0 ... n-1)
    start : line-graph index where the robot begins

    Returns
    -------
    A list of SnapNodes (never None/empty for n >= 1) describing one
    newly-explored node per step, from the start (layer 0) to the final
    explored interval [path[-1].i, path[-1].j]. Nodes outside that
    interval are never visited (see `skipped_nodes`). path[-1].count is
    the number of nodes that were visited on time; compare it to
    len(nodes) to see whether every deadline was met (the classic
    feasibility question from Algorithm 1 is exactly the case
    path[-1].count == len(nodes)).
    """
    n = len(nodes)
    if n == 0:
        return []

    # pos[k] = distance from node 0 to node k along the line, so the travel
    # time between any two nodes is just abs(pos[a] - pos[b]).
    pos = [0.0] * n
    for k in range(1, n):
        pos[k] = pos[k - 1] + nodes[k - 1].weight_right

    # dp[(i, j, side)][c] = (time, parent_key, parent_c) or None.
    # c ranges over 0..layer+1 on-time visits accumulated while exploring
    # interval [i, j] (layer = j - i). Keeping one slot per achievable
    # count (rather than only the overall best time) is what lets the
    # search recover from a missed deadline instead of giving up: a path
    # that skipped an on-time visit earlier is still tracked, in case it
    # allows catching more deadlines later on.
    dp = {}
    for i in range(n):
        for j in range(i, n):
            for side in (LEFT, RIGHT):
                dp[(i, j, side)] = [None] * (j - i + 2)

    # InitStart: the robot starts at 'start' at time 0, having "on-time
    # visited" itself (count = 1).
    for side in (LEFT, RIGHT):
        dp[(start, start, side)][1] = (0.0, None, None)

    # Relax layer by layer (layer = j - i), exactly like Algorithm 1, but
    # never discarding a transition just because a deadline was missed.
    for layer in range(n - 1):
        for i in range(n - layer):
            j = i + layer
            for side in (LEFT, RIGHT):
                arr = dp[(i, j, side)]
                robot_pos = i if side == LEFT else j

                neighbors = []
                if i > 0:
                    neighbors.append((i - 1, j, LEFT, i - 1))
                if j < n - 1:
                    neighbors.append((i, j + 1, RIGHT, j + 1))

                for c, entry in enumerate(arr):
                    if entry is None:
                        continue
                    t_src = entry[0]
                    for di, dj, dside, new_idx in neighbors:
                        t_dst    = t_src + abs(pos[new_idx] - pos[robot_pos])
                        deadline = nodes[new_idx].deadline
                        new_c    = c + 1 if t_dst <= deadline else c

                        dst_arr = dp[(di, dj, dside)]
                        if dst_arr[new_c] is None or t_dst < dst_arr[new_c][0]:
                            dst_arr[new_c] = (t_dst, (i, j, side), c)

    # The robot may stop at ANY state, not only once the whole line is
    # explored. Pick the highest on-time count; break ties by the shortest
    # time, then by the smaller interval (only matters with 0-weight edges).
    # This is what stops the robot from walking out to an end node that
    # has already expired: the same count is reachable sooner without it.
    best = None  # (count, -time, -layer, key)
    for key, arr in dp.items():
        i, j, _ = key
        for c, entry in enumerate(arr):
            if entry is None:
                continue
            cand = (c, -entry[0], -(j - i), key)
            if best is None or cand[:3] > best[:3]:
                best = cand

    achieved_count, _, _, key = best

    # Reconstruct the path by following parent pointers back to the start.
    path = []
    cur_key, cur_c = key, achieved_count
    while cur_key is not None:
        t, parent_key, parent_c = dp[cur_key][cur_c]
        i, j, side = cur_key
        on_time = parent_c is None or cur_c == parent_c + 1
        path.append(SnapNode(i, j, side, t, cur_c, on_time))
        cur_key, cur_c = parent_key, parent_c
    path.reverse()
    return path


# ── convenience helpers ────────────────────────────────────────────────────────

def move_sequence(path: list) -> list:
    """
    Extract the ordered sequence of line-graph node indices visited
    along the given path (one entry per snap node, including the start).
    """
    return [sn.newly_explored for sn in path]


def skipped_nodes(path: list, nodes: list) -> list:
    """Indices of the nodes the robot never reaches (outside the final interval)."""
    if not path:
        return list(range(len(nodes)))
    lo, hi = path[-1].i, path[-1].j
    return [k for k in range(len(nodes)) if k < lo or k > hi]


def is_fully_feasible(path: list, nodes: list) -> bool:
    """True if every node of the line was visited before its deadline."""
    return bool(path) and path[-1].count == len(nodes)
