"""
input_handler.py
================
Loads the line graph for the line exploration program from a .txt file.

The only way to provide a graph is a file: a welcome message is printed,
then the user presses Enter to open the file-picker. If the chosen file is
invalid, the error is printed and the user is prompted again. Closing the
picker without choosing a file (or Ctrl+C at the prompt) exits the program.

Returns a (nodes, start) tuple ready to pass to ExplorationViz.

File format expected
--------------------
  Line 1: start node index          (single integer, 0-based)
  Line 2: node deadlines            (comma-separated floats, one per node)
  Line 3: edge weights              (comma-separated floats, must be len(deadlines)-1)

Example
-------
  4
  60,60,60,60,60,60,60,60,60,60,60,60
  2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog
from line_exploration import Node

# Folder the file-picker opens in (falls back to the current directory).
INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")


# ── public entry point ─────────────────────────────────────────────────────────

def ask_for_input():
    """
    Print the welcome message, then (after Enter) open the file-picker until a valid
    graph file is chosen, and return (nodes, start).

    Exits the program if the picker is closed without choosing a file.
    """
    _print_welcome()

    while True:
        _wait_for_enter()
        try:
            return _load_from_file()
        except ValueError as e:
            print(f"\n  ✗  {e}")
            print("     Choose another file.\n")


# ── welcome message ────────────────────────────────────────────────────────────

def _print_welcome():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║          LINE EXPLORATION            ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    print("  Welcome! A single robot explores a line graph whose nodes")
    print("  have deadlines, visiting as many nodes on time as possible.")
    print()
    print("  The graph is loaded from a .txt file:")
    print("    line 1: start node index (0-based)")
    print("    line 2: node deadlines   (comma-separated)")
    print("    line 3: edge weights     (comma-separated, one fewer than nodes)")
    print()


def _wait_for_enter():
    try:
        input("  Press Enter to choose a graph file… ")
    except (EOFError, KeyboardInterrupt):
        print("\n  Exiting.")
        sys.exit(0)


# ── file loading ───────────────────────────────────────────────────────────────

def _load_from_file():
    # Open a native file-picker dialog. The hidden root window is marked
    # "topmost" so the dialog opens in front of the terminal.
    _root = tk.Tk()
    _root.attributes("-topmost", True)
    _root.lift()
    _root.focus_force()
    _root.withdraw()
    path = filedialog.askopenfilename(
        parent=_root,
        title="Select line graph file",
        initialdir=INPUTS_DIR if os.path.isdir(INPUTS_DIR) else os.getcwd(),
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    _root.destroy()

    if not path:
        print("  No file selected — exiting.")
        sys.exit(0)

    # Blank lines are ignored so minor formatting differences don't matter
    with open(path, "r") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]

    if len(lines) != 3:
        raise ValueError(
            f"File must have exactly 3 non-empty lines "
            f"(start node, deadlines, edge weights). "
            f"Got {len(lines)} line(s)."
        )

    # ── line 1: start node ────────────────────────────────────────────────
    try:
        start = int(lines[0])
    except ValueError:
        raise ValueError(
            f"Line 1 must be a single integer (start node). Got: '{lines[0]}'"
        )

    if start < 0:
        raise ValueError(f"Start node must be >= 0. Got: {start}")

    # ── line 2: deadlines ─────────────────────────────────────────────────
    deadlines = _parse_floats(lines[1], "deadlines (line 2)")
    n = len(deadlines)

    if n == 0:
        raise ValueError("Line 2 (deadlines) must contain at least one value.")

    # ── line 3: edge weights ──────────────────────────────────────────────
    weights = _parse_floats(lines[2], "edge weights (line 3)")

    # Validation rules
    if start >= n:
        raise ValueError(
            f"Start node is {start}, but only {n} node(s) exist "
            f"(valid indices are 0 to {n - 1})."
        )

    expected_edges = n - 1
    if len(weights) != expected_edges:
        raise ValueError(
            f"Number of edge weights must be exactly (nodes - 1) = {expected_edges}. "
            f"Got {len(weights)}."
        )

    if any(v < 0 for v in deadlines + weights):
        raise ValueError("Deadlines and edge weights must not be negative.")

    nodes = _build_nodes(deadlines, weights)
    _print_summary(nodes, start, source=f"file '{path}'")
    return nodes, start


# ── shared helpers ─────────────────────────────────────────────────────────────

def _parse_floats(raw: str, label: str) -> list:
    """Parse a comma-separated string into a list of floats."""
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    try:
        values = [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"Could not parse {label}: '{raw}' — all values must be numbers.")
    return values


def _build_nodes(deadlines: list, weights: list) -> list:
    """Combine deadline and weight lists into Node objects."""
    n     = len(deadlines)
    nodes = []
    for i in range(n):
        w = weights[i] if i < len(weights) else 0.0
        nodes.append(Node(index=i, deadline=deadlines[i], weight_right=w))
    return nodes


def _print_summary(nodes: list, start: int, source: str):
    print()
    print(f"  ✓  Loaded from {source}")
    print(f"     Nodes   : {len(nodes)}")
    print(f"     Start   : {start}")
    print(f"     Deadlines: {[nd.deadline for nd in nodes]}")
    print(f"     Weights  : {[nd.weight_right for nd in nodes[:-1]]}")
