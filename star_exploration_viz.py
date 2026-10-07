"""
star_exploration_viz.py
========================
Interactive step-by-step visualizer for the star exploration algorithm.

Requires star_exploration.py and star_input_handler.py in the same directory.
Run with:  python star_exploration_viz.py

Controls
--------
  [▶ STEP]   — send the robot from the center to the next leaf in the
               deadline-ordered visiting sequence
  [↺ RESET]  — restart the simulation from scratch

Color key
---------
  green   node  — visited, deadline met
  red     node  — expired: deadline passed before the robot got there
  gray    node  — not visited yet
  blue    node  — the robot's current position
"""

import math
import tkinter as tk
from tkinter import font as tkfont

from star_exploration     import explore_star, is_fully_feasible, skipped_leaves
from star_input_handler   import ask_for_input


# ── visual constants ───────────────────────────────────────────────────────────

PALETTE = {
    "bg":            "#0d0f14",
    "panel":         "#13161e",
    "node_idle":     "#1e2330",
    "node_border":   "#2e3550",
    "node_visited":  "#1a3a2a",
    "node_vis_brd":  "#2dde98",
    "node_skip":     "#1a1216",
    "node_skip_brd": "#ff5c6c",
    "text_red":      "#ff5c6c",
    "node_robot":    "#0f2744",
    "node_rob_brd":  "#4da6ff",
    "edge":          "#2a2f42",
    "edge_done":     "#2dde98",
    "text_main":     "#e8eaf2",
    "text_dim":      "#4a5070",
    "text_green":    "#2dde98",
    "text_blue":     "#4da6ff",
    "text_warn":     "#ffb347",
    "btn_step":      "#1a3a5c",
    "btn_step_h":    "#1e4a75",
    "btn_reset":     "#2a1a1a",
    "btn_reset_h":   "#3a2020",
    "accent":        "#4da6ff",
}

CANVAS_SIZE = 480   # square canvas, px
CENTER_R    = 30    # center-node circle radius (px)
LEAF_R      = 24    # leaf-node circle radius (px)
ORBIT_R     = 170   # distance from center to each leaf (px)
SIDE_W      = 320   # width of the right-hand info/buttons column (px)


# ── visualizer class ───────────────────────────────────────────────────────────

class StarExplorationViz:
    """
    Tkinter window that drives a step-by-step replay of the leaf-visiting
    order returned by star_exploration.explore_star().
    """

    def __init__(self, root: tk.Tk, leaves: list):
        self.root   = root
        self.leaves = leaves
        self.n      = len(leaves)

        root.title("Star Exploration — Step Visualizer")
        root.configure(bg=PALETTE["bg"])
        root.resizable(False, False)

        self._init_fonts()
        self._compute_layout()
        self._build_header()

        # Body: graph on the left, info panel + buttons in a column on the
        # right, so the window stays short enough for the buttons to show.
        body = tk.Frame(root, bg=PALETTE["bg"])
        body.pack(padx=20, pady=(0, 16))
        self._build_canvas(body)
        side = tk.Frame(body, bg=PALETTE["bg"], width=SIDE_W)
        side.pack(side="left", fill="y", padx=(16, 0))
        self._build_info_panel(side)
        self._build_buttons(side)

        self._init_sim()
        self._draw()

    # ── fonts ──────────────────────────────────────────────────────────────────

    def _init_fonts(self):
        self.f_title = tkfont.Font(family="Courier New", size=13, weight="bold")
        self.f_label = tkfont.Font(family="Courier New", size=10)
        self.f_small = tkfont.Font(family="Courier New", size=9)
        self.f_btn   = tkfont.Font(family="Courier New", size=11, weight="bold")
        self.f_info  = tkfont.Font(family="Courier New", size=10)

    # ── layout ─────────────────────────────────────────────────────────────────

    def _compute_layout(self):
        self.cw = CANVAS_SIZE
        self.ch = CANVAS_SIZE
        self.center_xy = (self.cw // 2, self.ch // 2)

        # leaf i (1-based) sits at angle starting from the top, going
        # clockwise around the center.
        self.leaf_xy = {}
        for i in range(self.n):
            angle = math.pi / 2 - 2 * math.pi * i / self.n
            cx, cy = self.center_xy
            x = cx + ORBIT_R * math.cos(angle)
            y = cy - ORBIT_R * math.sin(angle)
            self.leaf_xy[i + 1] = (x, y)

    # ── widget construction ────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=PALETTE["bg"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="◈  STAR EXPLORATION  ◈",
                 font=self.f_title, bg=PALETTE["bg"],
                 fg=PALETTE["accent"]).pack()
        tk.Label(hdr, text="Single-robot · Deadline-constrained · Max on-time leaves",
                 font=self.f_small, bg=PALETTE["bg"],
                 fg=PALETTE["text_dim"]).pack()
        tk.Label(hdr, text="green = visited on time    red = expired before the robot got there",
                 font=self.f_small, bg=PALETTE["bg"],
                 fg=PALETTE["text_dim"]).pack()

    def _build_canvas(self, parent):
        self.canvas = tk.Canvas(parent, width=self.cw, height=self.ch,
                                bg=PALETTE["bg"], highlightthickness=0)
        self.canvas.pack(side="left")

    def _stat_row(self, parent, title, value, colour):
        """One 'TITLE  value' line in the info panel; returns the value label."""
        row = tk.Frame(parent, bg=PALETTE["panel"])
        row.pack(fill="x", pady=2)
        tk.Label(row, text=title, font=self.f_small, width=13, anchor="w",
                 bg=PALETTE["panel"], fg=PALETTE["text_dim"]).pack(side="left")
        lbl = tk.Label(row, text=value, font=self.f_title,
                       bg=PALETTE["panel"], fg=colour)
        lbl.pack(side="left")
        return lbl

    def _build_info_panel(self, parent):
        self.info_frame = tk.Frame(parent, bg=PALETTE["panel"],
                                   bd=0, padx=18, pady=14)
        self.info_frame.pack(fill="x")

        self.lbl_time = self._stat_row(self.info_frame, "ELAPSED TIME", "0.00",
                                       PALETTE["text_blue"])
        self.lbl_pos  = self._stat_row(self.info_frame, "ROBOT AT", "center",
                                       PALETTE["accent"])
        self.lbl_step = self._stat_row(self.info_frame, "STEP", "0",
                                       PALETTE["text_main"])

        tk.Frame(self.info_frame, bg=PALETTE["node_border"],
                 height=1).pack(fill="x", pady=10)

        self.log_var = tk.StringVar(value="Waiting for first step…")
        tk.Label(self.info_frame, textvariable=self.log_var,
                 font=self.f_info, bg=PALETTE["panel"],
                 fg=PALETTE["text_main"], justify="left",
                 wraplength=SIDE_W - 36).pack(anchor="w")

        self.status_var = tk.StringVar(value="")
        tk.Label(self.info_frame, textvariable=self.status_var,
                 font=self.f_small, bg=PALETTE["panel"],
                 fg=PALETTE["text_dim"], justify="left",
                 wraplength=SIDE_W - 36).pack(anchor="w", pady=(6, 0))

    def _build_buttons(self, parent):
        btn_frame = tk.Frame(parent, bg=PALETTE["bg"], pady=16)
        btn_frame.pack()

        self.btn_step = self._make_btn(
            btn_frame, "▶  STEP",
            PALETTE["btn_step"], PALETTE["btn_step_h"],
            PALETTE["text_blue"], self._on_step,
        )
        self.btn_step.pack(side="left", padx=8)

        self._make_btn(
            btn_frame, "↺  RESET",
            PALETTE["btn_reset"], PALETTE["btn_reset_h"],
            PALETTE["text_warn"], self._on_reset,
        ).pack(side="left", padx=8)

    def _make_btn(self, parent, text, bg, hover_bg, fg, cmd):
        btn = tk.Label(parent, text=text, font=self.f_btn,
                       bg=bg, fg=fg, padx=22, pady=10,
                       cursor="hand2", relief="flat")
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e, b=btn, h=hover_bg: b.config(bg=h))
        btn.bind("<Leave>",    lambda e, b=btn, n=bg:       b.config(bg=n))
        return btn

    # ── simulation state ───────────────────────────────────────────────────────

    def _init_sim(self):
        """Compute the visiting order and reset all playback state."""
        self.path     = explore_star(self.leaves)   # only on-time visits
        self.achieved = len(self.path)
        self.fully_feasible = is_fully_feasible(self.path, self.leaves)
        self.skipped  = set(skipped_leaves(self.path, self.leaves))

        if self.fully_feasible:
            self.log_var.set(
                "Ready — every leaf can be reached on time. Press Step to begin.")
        else:
            self.log_var.set(
                f"Ready — at most {self.achieved}/{self.n} leaves can be reached on "
                f"time. Press Step to begin."
            )
        self.status_var.set("")

        # Playback cursors
        self.step_idx  = 0       # number of leaves visited so far
        self.robot_pos = 0       # 0 = center
        self.visited   = {0}     # leaf indices visited so far (0 = center)
        self.done      = False

    # ── drawing ────────────────────────────────────────────────────────────────

    def _current_time(self) -> float:
        return self.path[self.step_idx - 1].time if self.step_idx > 0 else 0.0

    def _expired(self, i: int) -> bool:
        """
        Red = not visited yet and its deadline has already passed. A skipped
        leaf whose deadline is still in the future when the run ends can't
        be reached in time either, so it turns red then.
        """
        if i in self.visited:
            return False
        if self.leaves[i - 1].deadline < self._current_time():
            return True
        return self.done and i in self.skipped

    def _newly_expired(self, t_before: float, t_after: float) -> list:
        return [lf.index for lf in self.leaves
                if lf.index not in self.visited
                and t_before <= lf.deadline < t_after]

    def _draw(self):
        c = self.canvas
        c.delete("all")
        cx, cy = self.center_xy
        expired = {i for i in range(1, self.n + 1) if self._expired(i)}

        # edges: center -> each leaf
        for i in range(1, self.n + 1):
            lx, ly = self.leaf_xy[i]
            done   = i in self.visited
            colour = PALETTE["edge_done"] if done else PALETTE["edge"]
            width  = 3 if done else 2
            dash   = (4, 4) if i in expired else None
            c.create_line(cx, cy, lx, ly, fill=colour, width=width, dash=dash)

            mx, my = (cx + lx) / 2, (cy + ly) / 2
            dx, dy = lx - cx, ly - cy
            length = math.hypot(dx, dy) or 1
            px, py = -dy / length * 16, dx / length * 16
            c.create_text(mx + px, my + py, text=f"w={self.leaves[i-1].weight}",
                          font=self.f_small, fill=PALETTE["text_dim"])

        # center node
        is_robot_center = (self.robot_pos == 0) and not self.done
        if is_robot_center:
            fill, border, bwidth = (PALETTE["node_robot"], PALETTE["node_rob_brd"], 3)
        else:
            fill, border, bwidth = (PALETTE["node_visited"], PALETTE["node_vis_brd"], 2)
        c.create_oval(cx - CENTER_R, cy - CENTER_R, cx + CENTER_R, cy + CENTER_R,
                      fill=fill, outline=border, width=bwidth)
        c.create_text(cx, cy, text="C", font=self.f_label,
                      fill=PALETTE["text_blue"] if is_robot_center else PALETTE["text_main"])

        # leaf nodes
        for i in range(1, self.n + 1):
            lx, ly = self.leaf_xy[i]
            leaf   = self.leaves[i - 1]
            is_robot = (i == self.robot_pos) and not self.done
            visited  = i in self.visited

            if is_robot:
                fill, border, bwidth = (PALETTE["node_robot"],
                                        PALETTE["node_rob_brd"], 3)
            elif visited:
                fill, border, bwidth = (PALETTE["node_visited"],
                                        PALETTE["node_vis_brd"], 2)
            elif i in expired:
                fill, border, bwidth = (PALETTE["node_skip"],
                                        PALETTE["node_skip_brd"], 2)
            else:
                fill, border, bwidth = (PALETTE["node_idle"],
                                        PALETTE["node_border"], 2)

            if is_robot:
                c.create_oval(lx - LEAF_R - 8, ly - LEAF_R - 8,
                              lx + LEAF_R + 8, ly + LEAF_R + 8,
                              outline=PALETTE["node_rob_brd"], width=1, dash=(4, 4))

            c.create_oval(lx - LEAF_R, ly - LEAF_R, lx + LEAF_R, ly + LEAF_R,
                          fill=fill, outline=border, width=bwidth)
            c.create_text(lx, ly, text=str(i), font=self.f_label,
                          fill=PALETTE["text_blue"] if is_robot else PALETTE["text_main"])

            if visited:
                label_colour = PALETTE["text_green"]
            elif i in expired:
                label_colour = PALETTE["text_red"]
            else:
                label_colour = PALETTE["text_dim"]

            dx, dy = lx - cx, ly - cy
            length = math.hypot(dx, dy) or 1
            label_x = lx + dx / length * (LEAF_R + 16)
            label_y = ly + dy / length * (LEAF_R + 16)
            c.create_text(label_x, label_y, text=f"d={leaf.deadline}",
                          font=self.f_small, fill=label_colour)

        # progress bar
        total = max(len(self.path), 1)
        frac  = self.step_idx / total
        bx1, by1 = 40, self.ch - 16
        bx2, by2 = self.cw - 40, self.ch - 8
        c.create_rectangle(bx1, by1, bx2, by2, fill=PALETTE["node_idle"], outline="")
        if frac > 0:
            c.create_rectangle(bx1, by1, bx1 + (bx2 - bx1) * frac, by2,
                                fill=PALETTE["text_green"], outline="")

    def _refresh_labels(self):
        cur_time = self._current_time()
        self.lbl_time.config(text=f"{cur_time:.2f}")
        self.lbl_pos.config(text="center" if self.robot_pos == 0 else f"leaf {self.robot_pos}")
        self.lbl_step.config(text=str(self.step_idx))

    # ── button handlers ────────────────────────────────────────────────────────

    def _on_step(self):
        if self.step_idx >= len(self.path):
            if not self.path:
                self.log_var.set("■  No leaf can be reached before its deadline — nothing to visit.")
            elif self.fully_feasible:
                self.log_var.set(
                    "✓  Exploration complete! Every leaf was visited within its deadline.")
            else:
                self.log_var.set(
                    f"■  Exploration complete — {self.achieved}/{self.n} leaves visited "
                    f"on time, the maximum possible (Algorithm 3). Skipped: "
                    f"{sorted(self.skipped)}."
                )
            self.status_var.set(f"Total time: {self._current_time():.2f}")
            self.btn_step.config(fg=PALETTE["text_dim"])
            self.done = True
            self._draw()
            return

        t_before = self._current_time()
        step = self.path[self.step_idx]
        self.step_idx += 1
        self.robot_pos = step.leaf_index
        self.visited.add(self.robot_pos)

        expired_now = self._newly_expired(t_before, step.time)
        self.log_var.set(
            f"Step {self.step_idx}:  center → leaf {step.leaf_index}  →  "
            f"arrived at time {step.time:.2f}  (deadline {step.deadline}, "
            f"ON TIME, slack {step.deadline - step.time:.2f})"
            + (f"\nExpired during this move: leaf/leaves {expired_now}" if expired_now else "")
        )

        # Every visited leaf is on time, so step_idx is also the on-time count.
        remaining = len(self.path) - self.step_idx
        if remaining == 0:
            self.done = True
            self.status_var.set(
                f"{self.step_idx}/{self.n} on time — press Reset to run again.")
        else:
            self.status_var.set(
                f"{remaining} leaf/leaves remaining · {self.step_idx}/{self.n} on time so far.")

        self._draw()
        self._refresh_labels()

    def _on_reset(self):
        self._init_sim()
        self._refresh_labels()
        self._draw()
        self.btn_step.config(fg=PALETTE["text_blue"])


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    leaves = ask_for_input()

    root = tk.Tk()
    StarExplorationViz(root, leaves)
    root.lift()
    root.focus_force()
    root.mainloop()
