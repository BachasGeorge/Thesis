import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Button

from LineGraph import BotSimulation          # reuse all logic from LineGraph.py

# ────── Config ──────

SIZE          = 20
VALUE_RANGE   = (80, 150)
EDGE_RANGE    = (1, 5)

# ────── Colors ──────

COLOR_UNVISITED = "#D3D1C7"
COLOR_VISITED   = "#378ADD"
COLOR_BOT       = "#639922"
COLOR_TARGET    = "#BA7517"
COLOR_EXPIRED   = "#E24B4A"
COLOR_EDGE      = "#B4B2A9"
COLOR_EDGE_MOVE = "#639922"
COLOR_TEXT      = "white"
COLOR_BG        = "#FAFAF8"
COLOR_BTN_STEP  = "#378ADD"
COLOR_BTN_NEW   = "#888780"

# ────── Layout helpers ──────

NODE_Y = 0.54


def node_x(i, n, pad=0.05):
    return pad + i * (1 - 2 * pad) / (n - 1)


# ────── Drawing ──────

def draw(ax, sim):
    ax.clear()
    ax.set_facecolor(COLOR_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    n   = sim.size
    xs  = [node_x(i, n) for i in range(n)]
    pos = sim.position
    tgt = sim.target
    exp = sim.expired_node
    frm = sim.last_from

    # ── edges ──
    for i in range(len(sim.edges)):
        x1, x2 = xs[i], xs[i + 1]
        active = frm != -1 and (
                (pos > frm == i) or
                (frm > pos and i == pos)
        )
        color = COLOR_EDGE_MOVE if active else COLOR_EDGE
        lw    = 2.5            if active else 1.5
        ax.plot([x1, x2], [NODE_Y, NODE_Y],
                color=color, lw=lw, zorder=1, solid_capstyle="round")
        ax.text((x1 + x2) / 2, NODE_Y + 0.10, str(sim.edges[i]),
                ha="center", va="center", fontsize=7, color="#888780")

    # ── target arc ──
    if tgt != -1 and exp == -1 and not sim.done:
        bx, tx = xs[pos], xs[tgt]
        ax.annotate(
            "", xy=(tx, NODE_Y + 0.045), xytext=(bx, NODE_Y + 0.045),
            arrowprops=dict(
                arrowstyle="->", color=COLOR_TARGET, lw=1.5,
                connectionstyle="arc3,rad=-0.4",
            ),
            zorder=2,
        )
        ax.text((bx + tx) / 2, NODE_Y + 0.30, "target",
                ha="center", va="center", fontsize=8, color=COLOR_TARGET)

    # ── nodes ──
    for i in range(n):
        x = xs[i]
        if i == exp:
            color = COLOR_EXPIRED
        elif i == pos:
            color = COLOR_BOT
        elif i == tgt and exp == -1 and not sim.done:
            color = COLOR_TARGET
        elif sim.nodes[i][1] == 1:
            color = COLOR_VISITED
        else:
            color = COLOR_UNVISITED

        circle = plt.Circle((x, NODE_Y), 0.030, color=color, zorder=3)
        ax.add_patch(circle)
        ax.text(x, NODE_Y, str(i),
                ha="center", va="center", fontsize=8,
                color=COLOR_TEXT, fontweight="bold", zorder=4)
        ax.text(x, NODE_Y - 0.12, str(sim.nodes[i][0]),
                ha="center", va="center", fontsize=7, color="#5F5E5A")

    # ── legend ──
    ax.legend(
        handles=[
            mpatches.Patch(color=COLOR_BOT,       label="Bot"),
            mpatches.Patch(color=COLOR_VISITED,   label="Visited"),
            mpatches.Patch(color=COLOR_TARGET,    label="Target"),
            mpatches.Patch(color=COLOR_EXPIRED,   label="Expired"),
            mpatches.Patch(color=COLOR_UNVISITED, label="Unvisited"),
        ],
        loc="upper center", ncol=5, fontsize=7.5,
        framealpha=0.85, edgecolor="#D3D1C7",
        bbox_to_anchor=(0.5, 0.98),
    )

    # ── status message ──
    if sim.done and not sim.failed:
        msg_text  = "All nodes visited successfully!"
        msg_color = "#27500A"
        msg_bg    = "#EAF3DE"
    elif sim.failed:
        msg_text  = f"Node {exp} expired — mission failed!"
        msg_color = "#A32D2D"
        msg_bg    = "#FCEBEB"
    elif sim.step_count == 0:
        msg_text  = f"Start: node {pos}   |   First target: {tgt}"
        msg_color = "#444441"
        msg_bg    = "#F1EFE8"
    else:
        msg_text  = f"Step {sim.step_count}: moved {frm} → {pos}   |   Next target: {tgt}"
        msg_color = "#444441"
        msg_bg    = "#F1EFE8"

    ax.text(0.5, 0.10, msg_text,
            ha="center", va="center", fontsize=9, color=msg_color,
            bbox=dict(boxstyle="round,pad=0.35", facecolor=msg_bg,
                      edgecolor="#D3D1C7", lw=0.8))

    # ── counters ──
    ax.text(0.02, 0.03,
            f"Visited: {sim.visited_count}/{n}",
            ha="left", va="bottom", fontsize=7.5, color="#888780")
    ax.text(0.98, 0.03,
            f"Step: {sim.step_count}",
            ha="right", va="bottom", fontsize=7.5, color="#888780")

    ax.figure.canvas.draw_idle()


# ────── Main ──────

def main():
    sim = BotSimulation(size=SIZE, value_range=VALUE_RANGE, edge_range=EDGE_RANGE)

    # Figure: tall enough for graph + two buttons below
    fig = plt.figure(figsize=(14, 5))
    fig.patch.set_facecolor(COLOR_BG)

    ax_graph = fig.add_axes([0.01, 0.18, 0.98, 0.80])   # main graph area
    ax_step  = fig.add_axes([0.38, 0.04, 0.14, 0.09])   # "Step" button
    ax_new   = fig.add_axes([0.54, 0.04, 0.08, 0.09])   # "New" button

    # ── Step button ──
    btn_step = Button(ax_step, "▶  Step", color=COLOR_BTN_STEP, hovercolor="#185FA5")
    btn_step.label.set_color("white")
    btn_step.label.set_fontsize(10)

    def on_step(_event):
        if not sim.done:
            sim.advance()
        draw(ax_graph, sim)

    btn_step.on_clicked(on_step)

    # ── New simulation button ──
    btn_new = Button(ax_new, "New", color=COLOR_BTN_NEW, hovercolor="#5F5E5A")
    btn_new.label.set_color("white")
    btn_new.label.set_fontsize(10)

    def on_new(_event):
        nonlocal sim
        sim = BotSimulation(size=SIZE, value_range=VALUE_RANGE, edge_range=EDGE_RANGE)
        draw(ax_graph, sim)

    btn_new.on_clicked(on_new)

    # ── Initial draw ──
    draw(ax_graph, sim)
    fig.suptitle("Node Traversal Bot  —  step-by-step",
                 fontsize=11, color="#2C2C2A", y=0.995)
    plt.show()


if __name__ == "__main__":
    main()
