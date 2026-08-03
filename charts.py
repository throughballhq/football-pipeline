"""The Throughball — reusable chart templates on top of brand.py.

All functions take plain data structures and a save path; no DB access here.
newsletter_pack.py (and later social/one-off scripts) feed them real data.
"""

import numpy as np
import matplotlib.pyplot as plt

import brand
from brand import INK, AQUA, LIME, WHITE, CONTEXT, TEXT_MUTED


# ------------------------------------------------------------------ radar

def radar_compare(title: str, subtitle: str, axes_labels: list,
                  player_a: tuple, player_b: tuple, path: str):
    """Two-player comparison radar.

    player_a/player_b: (name, [values 0-100 matching axes_labels]).
    Player A is the story -> lime. Player B is the reference -> aqua.
    Values should be percentiles vs. positional peers, computed by caller.
    """
    fig, ax = brand.new_chart(title, subtitle, size="square")
    ax.remove()
    ax = fig.add_axes([0.14, 0.06, 0.72, 0.64], polar=True)
    ax.set_facecolor(brand.BG)

    n = len(axes_labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    for (name, values), color, z in ((player_b, AQUA, 3), (player_a, LIME, 4)):
        vals = list(values) + [values[0]]
        ax.plot(angles, vals, color=color, lw=2.4, zorder=z)
        ax.fill(angles, vals, color=color, alpha=0.18, zorder=z)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_labels, color=TEXT_MUTED, fontsize=9.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75])
    ax.set_yticklabels(["25", "50", "75"], color=TEXT_MUTED, fontsize=7.5)
    ax.grid(color=brand.GRID, alpha=0.7)
    ax.spines["polar"].set_color(brand.GRID)

    fig.text(0.14, 0.78, f"—  {player_a[0]}", color=LIME, fontsize=11, fontweight="bold")
    fig.text(0.14, 0.745, f"—  {player_b[0]}", color=AQUA, fontsize=11, fontweight="bold")
    brand.finish(fig, path)


# --------------------------------------------------------------- heatmap

def fixture_heatmap(title: str, subtitle: str, team_names: list,
                    gw_labels: list, matrix, path: str, highlights=None):
    """Difficulty heatmap. matrix: rows=teams, cols=gws, values 1-5 or None
    (None = blank GW, rendered as canvas). highlights: [(row, col), ...]
    cells framed in lime — the story."""
    data = np.array([[v if v is not None else np.nan for v in row] for row in matrix],
                    dtype=float)
    h = max(6.0, 0.42 * len(team_names) + 2.6)
    fig, ax = brand.new_chart(title, subtitle, figsize=(10, h))
    cmap = brand.difficulty_cmap()
    cmap.set_bad(brand.BG)
    im = ax.imshow(data, cmap=cmap, vmin=1, vmax=5, aspect="auto")
    ax.set_xticks(range(len(gw_labels)), gw_labels)
    ax.set_yticks(range(len(team_names)), team_names)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.grid(False)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not np.isnan(data[i, j]):
                v = int(data[i, j])
                ax.text(j, i, str(v), ha="center", va="center", fontsize=8.5,
                        color=INK if v <= 2 else WHITE, fontweight="bold")
    for (row, col) in (highlights or []):
        brand.highlight_cell(ax, col, row)
    cbar = fig.colorbar(im, ax=ax, shrink=0.6, ticks=[1.4, 4.6])
    cbar.ax.set_yticklabels(["easy", "hard"], color=TEXT_MUTED, fontsize=9)
    cbar.outline.set_visible(False)
    brand.finish(fig, path)


# --------------------------------------------------------------- scatter

def market_scatter(title: str, subtitle: str, points: list, path: str,
                   xlabel: str, ylabel: str, annotate_top: int = 5):
    """points: [(x, y, label), ...]. Top-N by y annotated in lime."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    fig, ax = brand.new_chart(title, subtitle)
    ax.scatter(xs, ys, s=38, color=AQUA, alpha=0.5, edgecolors="none")
    top = sorted(points, key=lambda p: p[1], reverse=True)[:annotate_top]
    ax.scatter([p[0] for p in top], [p[1] for p in top], s=80, color=LIME, zorder=5)
    for x, y, label in top:
        ax.annotate(label, (x, y), xytext=(7, 5), textcoords="offset points",
                    color=LIME, fontsize=9.5, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    brand.finish(fig, path)


# ----------------------------------------------------------------- movers

def movers_bar(title: str, subtitle: str, movers: list, path: str,
               unit: str = "£m"):
    """movers: [(name, delta), ...] mixed risers/fallers, sorted by caller.
    Risers lime, fallers muted aqua."""
    names = [m[0] for m in movers]
    deltas = [m[1] for m in movers]
    colors = [LIME if d > 0 else CONTEXT for d in deltas]
    fig, ax = brand.new_chart(title, subtitle, figsize=(10, 0.5 * len(movers) + 3))
    y = np.arange(len(movers))
    ax.barh(y, deltas, color=colors, height=0.62)
    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.axvline(0, color=brand.GRID, lw=1)
    ax.set_xlabel(f"7-day change ({unit})")
    for yi, d in zip(y, deltas):
        ax.text(d + (0.01 if d >= 0 else -0.01), yi, f"{d:+.1f}",
                va="center", ha="left" if d >= 0 else "right",
                color=WHITE, fontsize=9, fontweight="bold")
    brand.finish(fig, path)
