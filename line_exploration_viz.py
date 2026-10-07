"""
line_exploration_viz.py
=======================
Interactive step-by-step visualizer for the line exploration algorithm.

Requires line_exploration.py and input_handler.py in the same directory.
Run with:  python line_exploration_viz.py

Controls
--------
  [▶ STEP]   — advance the robot one node along the optimal path
  [↺ RESET]  — restart the simulation from scratch
"""

import tkinter as tk
from tkinter import font as tkfont

from line_exploration  import explore, move_sequence, is_fully_feasible, skipped_nodes
from input_handler     import ask_for_input


# ── visual constants ───────────────────────────────────────────────────────────

PALETTE = {
    "bg":           "#0d0f14",
    "panel":        "#13161e",
    "node_idle":    "#1e2330",
    "node_border":  "#2e3550",
    "node_visited": "#1a3a2a",
    "node_vis_brd": "#2dde98",
    "node_late":    "#3a2a12",
    "node_late_brd":"#ffb347",
    "node_skip":    "#1a1216",
    "node_skip_brd":"#ff5c6c",
    "text_red":     "#ff5c6c",
    "node_robot":   "#0f2744",
    "node_rob_brd": "#4da6ff",
    "edge":         "#2a2f42",
    "edge_done":    "#2dde98",
    "text_main":    "#e8eaf2",
    "text_dim":     "#4a5070",
    "text_green":   "#2dde98",
    "text_blue":    "#4da6ff",
    "text_warn":    "#ffb347",
    "btn_step":     "#1a3a5c",
    "btn_step_h":   "#1e4a75",
    "btn_reset":    "#2a1a1a",
    "btn_reset_h":  "#3a2020",
    "accent":       "#4da6ff",
}

NODE_R   = 30    # node circle radius (px)
MARGIN_X = 80    # left/right canvas margin (px)
MARGIN_Y = 100   # top/bottom canvas margin (px)
SPACING  = 140   # horizontal gap between node centres (px)


# ── visualizer class ───────────────────────────────────────────────────────────

class ExplorationViz:
    """
    Tkinter window that drives a step-by-step replay of the optimal
    exploration path returned by line_exploration.explore().
    """

    def __init__(self, root: tk.Tk, nodes: list, start: int):
        self.root  = root
        self.nodes = nodes
        self.start = start
        self.n     = len(nodes)

        root.title("Line Exploration — Step Visualizer")
        root.configure(bg=PALETTE["bg"])
        root.resizable(False, False)

        self._init_fonts()
        self._compute_canvas_size()
        self._build_header()
        self._build_canvas()
        self._build_info_panel()
        self._build_buttons()

        self._init_sim()
        self._draw()

    # ── fonts ──────────────────────────────────────────────────────────────────

    def _init_fonts(self):
        self.f_title = tkfont.Font(family="Courier New", size=13, weight="bold")
        self.f_label = tkfont.Font(family="Courier New", size=10)
        self.f_small = tkfont.Font(family="Courier New", size=9)
        self.f_btn   = tkfont.Font(family="Courier New", size=11, weight="bold")
        self.f_info  = tkfont.Font(family="Courier New", size=10)

    # ── canvas sizing ──────────────────────────────────────────────────────────

    def _compute_canvas_size(self):
        self.cw = MARGIN_X * 2 + SPACING * (self.n - 1)
        self.ch = MARGIN_Y * 2 + NODE_R * 2

    # ── widget construction ────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=PALETTE["bg"], pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="◈  LINE EXPLORATION  ◈",
                 font=self.f_title, bg=PALETTE["bg"],
                 fg=PALETTE["accent"]).pack()
        tk.Label(hdr, text="Single-robot · Deadline-constrained · Best-effort path",
                 font=self.f_small, bg=PALETTE["bg"],
                 fg=PALETTE["text_dim"]).pack()
        tk.Label(hdr, text="green = on time    orange = visited late (doesn't count)    red = expired before the robot got there",
                 font=self.f_small, bg=PALETTE["bg"],
                 fg=PALETTE["text_dim"]).pack()

    def _build_canvas(self):
        frame = tk.Frame(self.root, bg=PALETTE["bg"])
        frame.pack(padx=20)
        self.canvas = tk.Canvas(frame, width=self.cw, height=self.ch,
                                bg=PALETTE["bg"], highlightthickness=0)
        self.canvas.pack()

    def _build_info_panel(self):
        self.info_frame = tk.Frame(self.root, bg=PALETTE["panel"],
                                   bd=0, padx=24, pady=16)
        self.info_frame.pack(fill="x", padx=20, pady=(4, 0))

        row1 = tk.Frame(self.info_frame, bg=PALETTE["panel"])
        row1.pack(fill="x")

        tk.Label(row1, text="ELAPSED TIME", font=self.f_small,
                 bg=PALETTE["panel"], fg=PALETTE["text_dim"]).pack(side="left")
        self.lbl_time = tk.Label(row1, text="0.00", font=self.f_title,
                                 bg=PALETTE["panel"], fg=PALETTE["text_blue"])
        self.lbl_time.pack(side="left", padx=(8, 40))

        tk.Label(row1, text="ROBOT AT", font=self.f_small,
                 bg=PALETTE["panel"], fg=PALETTE["text_dim"]).pack(side="left")
        self.lbl_pos = tk.Label(row1, text=f"node {self.start}",
                                font=self.f_title,
                                bg=PALETTE["panel"], fg=PALETTE["accent"])
        self.lbl_pos.pack(side="left", padx=(8, 40))

        tk.Label(row1, text="STEP", font=self.f_small,
                 bg=PALETTE["panel"], fg=PALETTE["text_dim"]).pack(side="left")
        self.lbl_step = tk.Label(row1, text="0", font=self.f_title,
                                 bg=PALETTE["panel"], fg=PALETTE["text_main"])
        self.lbl_step.pack(side="left", padx=8)

        tk.Frame(self.info_frame, bg=PALETTE["node_border"],
                 height=1).pack(fill="x", pady=10)

        self.log_var = tk.StringVar(value="Waiting for first step…")
        tk.Label(self.info_frame, textvariable=self.log_var,
                 font=self.f_info, bg=PALETTE["panel"],
                 fg=PALETTE["text_main"], justify="left",
                 wraplength=self.cw - 20).pack(anchor="w")

        self.status_var = tk.StringVar(value="")
        tk.Label(self.info_frame, textvariable=self.status_var,
                 font=self.f_small, bg=PALETTE["panel"],
                 fg=PALETTE["text_dim"]).pack(anchor="w", pady=(6, 0))

    def _build_buttons(self):
        btn_frame = tk.Frame(self.root, bg=PALETTE["bg"], pady=16)
        btn_frame.pack()

        self.btn_step = self._make_btn(
            btn_frame, "▶  STEP",
            PALETTE["btn_step"], PALETTE["btn_step_h"],
            PALETTE["text_blue"], self._on_step,
        )
        self.btn_step.pack(side="left", padx=10)

        self._make_btn(
            btn_frame, "↺  RESET",
            PALETTE["btn_reset"], PALETTE["btn_reset_h"],
            PALETTE["text_warn"], self._on_reset,
        ).pack(side="left", padx=10)

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
        """Compute the best-effort exploration path and reset all playback state."""
        path = explore(self.nodes, self.start)

        self.path     = path
        self.moves    = move_sequence(path)   # list of node indices
        self.achieved = path[-1].count        # on-time visits in the full plan
        self.fully_feasible = is_fully_feasible(path, self.nodes)
        self.skipped  = set(skipped_nodes(path, self.nodes))

        if self.fully_feasible:
            self.log_var.set("Ready — every node can be reached on time. Press Step to begin.")
        else:
            self.log_var.set(
                f"Ready — best effort: {self.achieved}/{self.n} nodes reachable "
                f"before their deadline. Press Step to begin."
            )
        self.status_var.set("")

        # Playback cursors
        self.step_idx      = 0
        self.robot_pos      = self.start
        # node index -> True if visited on time, False if visited late (doesn't count)
        self.visited_status = {self.start: self.path[0].on_time}
        self.done           = False   # True once the last step has been taken

    # ── drawing ────────────────────────────────────────────────────────────────

    def _node_cx(self, idx: int) -> int:
        return MARGIN_X + idx * SPACING

    def _node_cy(self) -> int:
        return self.ch // 2

    def _current_time(self) -> float:
        return self.path[self.step_idx].time if self.path else 0.0

    def _expired(self, i: int) -> bool:
        """
        Red = not visited yet and its deadline has already passed. A node
        that is skipped but whose deadline is still in the future when the
        run ends can't be reached in time either, so it turns red then.
        """
        if i in self.visited_status:
            return False
        if self.nodes[i].deadline < self._current_time():
            return True
        return self.done and i in self.skipped

    def _newly_expired(self, t_before: float, t_after: float) -> list:
        return [k for k in range(self.n)
                if k not in self.visited_status
                and t_before <= self.nodes[k].deadline < t_after]

    def _draw(self):
        c  = self.canvas
        cy = self._node_cy()
        c.delete("all")

        # edges
        for i in range(self.n - 1):
            x1 = self._node_cx(i)
            x2 = self._node_cx(i + 1)
            both_done = (i in self.visited_status and i + 1 in self.visited_status)
            colour    = PALETTE["edge_done"] if both_done else PALETTE["edge"]
            c.create_line(x1, cy, x2, cy, fill=colour, width=3)
            mx = (x1 + x2) / 2
            c.create_text(mx, cy - 18,
                          text=f"w={self.nodes[i].weight_right}",
                          font=self.f_small, fill=PALETTE["text_dim"])

        # nodes
        for i in range(self.n):
            cx           = self._node_cx(i)
            nd           = self.nodes[i]
            is_robot     = (i == self.robot_pos) and not self.done
            visit_status = self.visited_status.get(i)   # None / True (on-time) / False (late)
            expired      = self._expired(i)

            if is_robot:
                fill, border, bwidth = (PALETTE["node_robot"],
                                        PALETTE["node_rob_brd"], 3)
            elif visit_status is True:
                fill, border, bwidth = (PALETTE["node_visited"],
                                        PALETTE["node_vis_brd"], 2)
            elif visit_status is False:
                fill, border, bwidth = (PALETTE["node_late"],
                                        PALETTE["node_late_brd"], 2)
            elif expired:
                fill, border, bwidth = (PALETTE["node_skip"],
                                        PALETTE["node_skip_brd"], 2)
            else:
                fill, border, bwidth = (PALETTE["node_idle"],
                                        PALETTE["node_border"], 2)

            if is_robot:
                c.create_oval(cx - NODE_R - 8, cy - NODE_R - 8,
                              cx + NODE_R + 8, cy + NODE_R + 8,
                              outline=PALETTE["node_rob_brd"], width=1,
                              dash=(4, 4))

            c.create_oval(cx - NODE_R, cy - NODE_R,
                          cx + NODE_R, cy + NODE_R,
                          fill=fill, outline=border, width=bwidth)

            c.create_text(cx, cy, text=str(i), font=self.f_label,
                          fill=PALETTE["text_blue"] if is_robot
                          else PALETTE["text_main"])

            if is_robot:
                c.create_text(cx, cy - NODE_R - 20, text="●",
                              font=self.f_label, fill=PALETTE["accent"])

            if visit_status is True:
                label_colour = PALETTE["text_green"]
            elif visit_status is False:
                label_colour = PALETTE["text_warn"]
            elif expired:
                label_colour = PALETTE["text_red"]
            else:
                label_colour = PALETTE["text_dim"]
            c.create_text(cx, cy + NODE_R + 14,
                          text=f"d={nd.deadline}", font=self.f_small,
                          fill=label_colour)

            if expired:
                c.create_text(cx, cy + NODE_R + 30, text="expired",
                              font=self.f_small, fill=PALETTE["text_red"])

        # progress bar
        total = max(len(self.moves) - 1, 1)
        frac  = self.step_idx / total
        bx1, by1 = MARGIN_X,          self.ch - 16
        bx2, by2 = self.cw - MARGIN_X, self.ch - 8
        c.create_rectangle(bx1, by1, bx2, by2,
                            fill=PALETTE["node_idle"], outline="")
        if frac > 0:
            c.create_rectangle(bx1, by1,
                                bx1 + (bx2 - bx1) * frac, by2,
                                fill=PALETTE["text_green"], outline="")

    def _refresh_labels(self):
        self.lbl_time.config(text=f"{self._current_time():.2f}")
        self.lbl_pos.config(text=f"node {self.robot_pos}")
        self.lbl_step.config(text=str(self.step_idx))

    # ── button handlers ────────────────────────────────────────────────────────

    def _on_step(self):
        if self.step_idx >= len(self.moves) - 1:
            if self.fully_feasible:
                self.log_var.set(
                    "✓  Exploration complete! Every node was visited within its deadline.")
            else:
                self.log_var.set(
                    f"■  Exploration complete — best effort: {self.achieved}/{self.n} "
                    f"nodes visited within their deadline."
                    + (f" Never visited (already expired): {sorted(self.skipped)}."
                       if self.skipped else "")
                )
            self.status_var.set(f"Total time: {self.path[-1].time:.2f}")
            self.btn_step.config(fg=PALETTE["text_dim"])
            self.done = True
            self._draw()
            return

        t_before = self._current_time()
        self.step_idx += 1
        sn           = self.path[self.step_idx]
        prev_pos     = self.robot_pos
        self.robot_pos = self.moves[self.step_idx]
        self.visited_status[self.robot_pos] = sn.on_time

        direction = "◄ left" if self.robot_pos < prev_pos else "► right"
        nd        = self.nodes[self.robot_pos]
        slack     = nd.deadline - sn.time

        if sn.on_time:
            outcome = f"ON TIME (slack {slack:.2f})"
        else:
            outcome = f"LATE by {-slack:.2f} — does not count"

        expired_now = self._newly_expired(t_before, sn.time)
        self.log_var.set(
            f"Step {self.step_idx}:  moved {direction}  →  "
            f"arrived at node {self.robot_pos} at time {sn.time:.2f}  "
            f"(deadline {nd.deadline}, {outcome})"
            + (f"\nExpired during this move: node(s) {expired_now}" if expired_now else "")
        )
        remaining = len(self.moves) - 1 - self.step_idx
        if remaining == 0:
            self.done = True
            self.status_var.set(
                f"{sn.count}/{self.n} on time — press Reset to run again.")
        else:
            self.status_var.set(
                f"{remaining} move(s) remaining · {sn.count}/{self.n} on time so far.")

        self._draw()
        self._refresh_labels()

    def _on_reset(self):
        self._init_sim()
        self._refresh_labels()
        self._draw()
        self.btn_step.config(fg=PALETTE["text_blue"])


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Welcome message + file-picker (see input_handler.py)
    nodes, start = ask_for_input()

    root = tk.Tk()
    ExplorationViz(root, nodes, start)
    root.lift()
    root.focus_force()
    root.mainloop()