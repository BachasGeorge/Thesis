"""
star_input_handler.py
======================
Loads the star graph for the star exploration program from a .txt file.

The only way to provide a graph is a file: a welcome message is printed,
then the user presses Enter to open the file-picker. If the chosen file is
invalid, the error is printed and the user is prompted again. Closing the
picker without choosing a file (or Ctrl+C at the prompt) exits the program.

Returns a list of Leaf objects ready to pass to StarExplorationViz. The
robot always starts at the center of the star (there's no "start node" to
choose, unlike the line graph).

File format expected
--------------------
  Line 1: leaf deadlines   (comma-separated floats, one per leaf)
  Line 2: edge weights     (comma-separated floats, same length as line 1;
                            weight[i] is the travel time between the
                            center and leaf i+1)

Example
-------
  6,9,14,25
  2,3,4,5
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog
from star_exploration import Leaf

# Folder the file-picker opens in (falls back to the current directory).
INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")


# ── public entry point ─────────────────────────────────────────────────────────

def ask_for_input():
    """
    Print the welcome message, then (after Enter) open the file-picker until a valid
    graph file is chosen, and return a list of Leaf objects.

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
    print("  ║          STAR EXPLORATION            ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    print("  Welcome! A single robot starts at the center of a star graph")
    print("  and visits as many leaves as possible before their deadlines.")
    print()
    print("  The graph is loaded from a .txt file:")
    print("    line 1: leaf deadlines (comma-separated)")
    print("    line 2: edge weights   (comma-separated, one per leaf)")
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
        title="Select star graph file",
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

    if len(lines) != 2:
        raise ValueError(
            f"File must have exactly 2 non-empty lines "
            f"(deadlines, edge weights). Got {len(lines)} line(s)."
        )

    deadlines = _parse_floats(lines[0], "deadlines (line 1)")
    n = len(deadlines)
    if n == 0:
        raise ValueError("Line 1 (deadlines) must contain at least one value.")

    weights = _parse_floats(lines[1], "edge weights (line 2)")
    if len(weights) != n:
        raise ValueError(
            f"Number of edge weights must equal the number of leaves ({n}). "
            f"Got {len(weights)}."
        )

    if any(v < 0 for v in deadlines + weights):
        raise ValueError("Deadlines and edge weights must not be negative.")

    leaves = _build_leaves(deadlines, weights)
    _print_summary(leaves, source=f"file '{path}'")
    return leaves


# ── shared helpers ─────────────────────────────────────────────────────────────

def _parse_floats(raw: str, label: str) -> list:
    """Parse a comma-separated string into a list of floats."""
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    try:
        values = [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"Could not parse {label}: '{raw}' — all values must be numbers.")
    return values


def _build_leaves(deadlines: list, weights: list) -> list:
    """Combine deadline and weight lists into Leaf objects (1-based index)."""
    return [Leaf(index=i + 1, deadline=deadlines[i], weight=weights[i])
            for i in range(len(deadlines))]


def _print_summary(leaves: list, source: str):
    print()
    print(f"  ✓  Loaded from {source}")
    print(f"     Leaves    : {len(leaves)}")
    print(f"     Deadlines : {[lf.deadline for lf in leaves]}")
    print(f"     Weights   : {[lf.weight for lf in leaves]}")
    print()
