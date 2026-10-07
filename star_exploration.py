"""

Core algorithm for single-robot star exploration with deadlines.

Based on two algorithms from:
  "Deadlines"
  Shantanu Das, Nikos Giachoudis, Flaminia L. Luccio, Euripides Markou

  * Algorithm 1 ("Star decision problem", Section 4.1) -- decides whether
    a set of leaves can ALL be visited on time, and gives the order.
  * Algorithm 3 ("Star optimization", Section 5.1) -- when not every leaf
    can be visited on time, picks the LARGEST set of leaves that can be,
    using Algorithm 1 as its feasibility test.

The star model: one center node and n leaves, each leaf connected only to
the center by an edge with a travel-time weight. The robot always starts
at the center. To go from one leaf to another it must pass back through
the center -- there is no direct leaf-to-leaf edge.

Algorithm 1 / Lemma 3 is an exchange argument: if there exists ANY order
in which a single robot can visit every leaf of a set before its deadline,
then visiting them in non-decreasing order of (deadline + edge weight) is
ALSO a feasible order. So the decision is exact.

Algorithm 3: go through the leaves in non-decreasing order of edge weight
(ties: larger deadline first) and keep a leaf only if the set chosen so
far plus that leaf is still feasible per Algorithm 1. The chosen set is
then visited in Algorithm 1's order, so every visited leaf is on time.

Leaves that are NOT chosen are never visited at all. On a star that costs
nothing: a leaf hangs off the center on its own edge, so skipping it
never blocks access to anything else, and walking to a leaf that is
already expired would only add travel time without adding to the count.
(Contrast with the line, where a late node in the middle of the explored
interval must still be walked through.)

"""

# ── data structures ────────────────────────────────────────────────────────────

class Leaf:
    """
    A leaf node of the star graph.

    Parameters
    ----------
    index    : leaf id (1-based; 0 is reserved for the center)
    deadline : latest time the robot may arrive here
    weight   : travel time of the single edge connecting this leaf to the
               center (traversed once each way)
    """
    def __init__(self, index: int, deadline: float, weight: float):
        self.index    = index
        self.deadline = deadline
        self.weight   = weight


class StarStep:
    """One visit in the resulting traversal order."""
    def __init__(self, leaf_index: int, time: float, deadline: float, on_time: bool):
        self.leaf_index = leaf_index
        self.time       = time      # arrival time at this leaf
        self.deadline   = deadline
        self.on_time    = on_time   # was this leaf's own deadline met?


# ── internal helpers ───────────────────────────────────────────────────────────

def _feasibility_order(leaves: list) -> list:
    """Algorithm 1's visiting order: non-decreasing (deadline + weight)."""
    return sorted(leaves, key=lambda lf: lf.deadline + lf.weight)


def _schedule(order: list) -> list:
    """Walk the leaves in the given order (center -> leaf -> center -> ...)."""
    path = []
    t = 0.0
    for k, leaf in enumerate(order):
        if k > 0:
            t += order[k - 1].weight   # back to the center from the previous leaf
        t += leaf.weight               # center -> this leaf
        path.append(StarStep(leaf.index, t, leaf.deadline, t <= leaf.deadline))
    return path


def is_feasible_set(leaves: list) -> bool:
    """Algorithm 1: can every leaf in `leaves` be visited on time?"""
    return all(step.on_time for step in _schedule(_feasibility_order(leaves)))


# ── main algorithm ─────────────────────────────────────────────────────────────

def explore_star(leaves: list):
    """
    Visit the largest possible set of leaves before their deadlines.

    Algorithm 3 picks the set (Algorithm 1 is the feasibility test inside
    it); the chosen leaves are then visited in Algorithm 1's order.
    Leaves outside the set are skipped entirely -- the robot never
    travels to them.

    Parameters
    ----------
    leaves : list of Leaf objects (any order)

    Returns
    -------
    A list of StarStep, one per VISITED leaf, in visiting order. Every
    step is on time. Leaves missing from the path were skipped (see
    `skipped_leaves`); the instance is fully feasible exactly when no
    leaf was skipped (see `is_fully_feasible`).
    """
    by_weight = sorted(leaves, key=lambda lf: (lf.weight, -lf.deadline))
    chosen = []
    for leaf in by_weight:
        if is_feasible_set(chosen + [leaf]):
            chosen.append(leaf)

    return _schedule(_feasibility_order(chosen))


# ── convenience helpers ────────────────────────────────────────────────────────

def leaf_sequence(path: list) -> list:
    """Ordered list of leaf indices visited along the given path."""
    return [step.leaf_index for step in path]


def skipped_leaves(path: list, leaves: list) -> list:
    """Indices of the leaves the robot never visits (sorted)."""
    visited = set(leaf_sequence(path))
    return sorted(lf.index for lf in leaves if lf.index not in visited)


def is_fully_feasible(path: list, leaves: list) -> bool:
    """True if every leaf of the star was visited before its deadline."""
    return len(path) == len(leaves)   # explore_star only returns on-time steps
