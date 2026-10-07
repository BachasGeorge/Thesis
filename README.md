# Graph Exploration with Deadlines

Simulations of a **single robot exploring a graph whose nodes have deadlines**.
Every edge has a travel time and every node has a deadline: a node counts only
if the robot reaches it **at or before** its deadline. For each graph type the
program answers two questions:

1. **Complete solution** – can *every* node be visited on time? If yes, what is
   the route (and, for the line, the fastest such route)?
2. **Best effort** – if not, what route visits the **largest possible number**
   of nodes on time?

The route is then replayed step by step in a small desktop window.

---

## Based on

| Paper | Used for |
|---|---|
| J. Czyzowicz, M. Godon, E. Kranakis, A. Labourel, E. Markou – *Exploring Graphs with Time Constraints by Unreliable Collections of Mobile Robots* (SOFSEM 2018) | **Line**, complete solution: Algorithm 1 (snapshot graph, shortest-time tree) |
| S. Das, N. Giachoudis, F. L. Luccio, E. Markou – *Deadlines* | **Star**: Algorithm 1 (complete) and Algorithm 3 (best effort). **2-star**: Algorithm 2 (complete). Problem 2 of this paper is also the goal of the line's best-effort version |
| S. Kanellopoulos, C. Pergaminelis, E. Markou et al. – *Finite Pinwheel Scheduling: the k-Visits Problem* | Background on scheduling with deadlines |
| R. Holte, A. Mok, L. Rosier, I. Tulchinsky, D. Varvel – *The Pinwheel: A Real-Time Scheduling Problem* | Background on scheduling with deadlines |

All four papers are in `Research material/`.

---

## How it works (short version)

### Line
The robot starts at a chosen node. Whatever it does, the set of explored nodes
is always one continuous interval around the start, so every possible route is a
path in the paper's *snapshot graph* (state = explored interval + which end the
robot is at).

- **Complete solution** – exactly the paper's Algorithm 1: a layer-by-layer
  shortest-time search that only allows moves meeting the new node's deadline.
- **Best effort** (our extension) – the same search, but a late node does not
  stop the robot (it can pass through it, it just doesn't count). The search keeps
  the best time for every possible on-time count, then picks the route with the
  **most on-time nodes**, and among those the **fastest**. The robot stops as soon
  as nothing more can be gained, so it never walks out to an end node that has
  already expired. Expired nodes *between* useful ones are still walked through
  (on a line there is no way around them).

### Star
One center, leaves connected only to the center; the robot starts at the center
and returns through it between leaves.

- **Complete solution** – Algorithm 1: visit the leaves in non-decreasing order
  of `deadline + edge weight`. If that order fails, no order can succeed.
- **Best effort** – Algorithm 3: go through the leaves from lightest edge to
  heaviest and keep a leaf only if the kept set can still all be visited on time
  (checked with Algorithm 1). Leaves that are not kept are never visited.
  *Small fix vs. the paper:* the paper adds the first leaf without checking it,
  which is wrong if that leaf alone is unreachable; here every leaf is checked.

---

## Repository structure

```
line_exploration.py          line algorithm (complete + best effort)
input_handler.py             reads a line graph from a .txt file
line_exploration_viz.py      line visualizer            <- run this
star_exploration.py          star algorithm (complete + best effort)
star_input_handler.py        reads a star graph from a .txt file
star_exploration_viz.py      star visualizer            <- run this
inputs/                      example input files
Research material/           the papers
```

---

## Running it on your computer

### 1. Install Python
Python **3** is required (developed with Python 3.14). Download it from
[python.org](https://www.python.org/downloads/).

The windows use **tkinter**, which comes with Python on most systems:

- **Windows** – included with the python.org installer (keep the
  *tcl/tk and IDLE* option ticked). On the first installer screen also tick
  **"Add python.exe to PATH"**.
- **macOS** – included with the python.org installer. If you use Homebrew's
  Python instead: `brew install python-tk`.
- **Linux** – usually a separate package, e.g. on Ubuntu/Debian:
  `sudo apt install python3-tk`.

Check that it works:
```bash
python -m tkinter
```
A small test window should open. (On macOS/Linux you may need to type
`python3` instead of `python` in all commands.)

No other packages are needed – the code only uses Python's standard library.

### 2. Get the code
With git:
```bash
git clone https://github.com/BachasGeorge/Thesis.git
cd Thesis
```
Or on GitHub click **Code → Download ZIP**, unzip it, and open a terminal in the
unzipped folder.

### 3. Run a simulation
From inside the folder:
```bash
python line_exploration_viz.py      # line graph
python star_exploration_viz.py      # star graph
```

A welcome message is printed with the expected file format. Press
**Enter**, choose a graph file in the window that opens (it starts
in `inputs/`), and the visualizer appears. If the file is invalid,
the error is printed and you can choose another one; closing the file window exits.


In the visualizer, **STEP** moves the robot one node/leaf forward and **RESET**
starts over.

| Colour | Meaning |
|---|---|
| Blue   | robot's current position |
| Green  | visited on time |
| Orange | visited late – doesn't count (line only; the robot had to pass through it) |
| Red    | expired before the robot got there |
| Grey   | not visited yet |

---

## Input file format

Plain `.txt` files, values separated by commas. Blank lines are ignored.
Deadlines and weights must not be negative.

### Line – 3 lines
```
1              start node (0-based index)
7,5,6,11,13    deadline of each node, left to right
3,1,2,2        edge weights between consecutive nodes (one fewer than nodes)
```
(`inputs/line_paper_figure1.txt` – the Figure 1 example from the line paper.)

### Star – 2 lines
```
6,9,14,25      deadline of each leaf (leaf 1, leaf 2, ...)
2,3,4,5        weight of the edge center–leaf, same order
```
(`inputs/star_example.txt`)
