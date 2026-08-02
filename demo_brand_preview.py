"""Brand preview: three sample charts with plausible mock data.

Not part of the daily pipeline — run locally/once to evaluate the visual system.
"""

import numpy as np
import matplotlib.pyplot as plt

import brand
from brand import INK, AQUA, LIME, WHITE, CONTEXT, TEXT_MUTED

OUT = "/mnt/user-data/outputs"


def chart_fixture_heatmap():
    teams = ["Arsenal", "Man City", "Liverpool", "Chelsea", "Villa", "Newcastle",
             "Spurs", "Man Utd"]
    gws = [f"GW{i}" for i in range(1, 7)]
    rng = np.random.default_rng(7)
    data = rng.integers(1, 6, size=(len(teams), len(gws)))

    fig, ax = brand.new_chart(
        "Who has the kind run-in?",
        "Attacking fixture difficulty, next 6 gameweeks — our model, not the official FDR",
        size="std",
    )
    im = ax.imshow(data, cmap=brand.difficulty_cmap(), vmin=1, vmax=5, aspect="auto")
    ax.set_xticks(range(len(gws)), gws)
    ax.set_yticks(range(len(teams)), teams)
    ax.grid(False)
    for i in range(len(teams)):
        for j in range(len(gws)):
            v = data[i, j]
            ax.text(j, i, str(v), ha="center", va="center", fontsize=10,
                    color=INK if v <= 3 else WHITE, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, shrink=0.7, ticks=[1.4, 4.6])
    cbar.ax.set_yticklabels(["easy", "hard"], color=TEXT_MUTED, fontsize=9)
    cbar.outline.set_visible(False)
    brand.finish(fig, f"{OUT}/preview_fixture_heatmap.png")


def chart_xg_trend():
    rng = np.random.default_rng(3)
    gws = np.arange(1, 11)
    fig, ax = brand.new_chart(
        "Quietly becoming elite",
        "Rolling xGI per 90 — highlighted player vs. positional peers, GW1-10",
    )
    for _ in range(5):
        ax.plot(gws, np.clip(0.45 + rng.normal(0, 0.07, 10).cumsum() * 0.4, 0.1, 1.0),
                color=CONTEXT, lw=1.4, alpha=0.65)
    hero = np.clip(0.35 + np.linspace(0, 0.55, 10) + rng.normal(0, 0.03, 10), 0.2, 1.1)
    ax.plot(gws, hero, color=LIME, lw=3.2, solid_capstyle="round")
    ax.scatter(gws[-1], hero[-1], color=LIME, s=55, zorder=5)
    ax.annotate("Semenyo  0.86", (gws[-1], hero[-1]), xytext=(-64, 12),
                textcoords="offset points", color=LIME, fontsize=11, fontweight="bold")
    ax.set_xticks(gws, [f"GW{g}" for g in gws])
    ax.set_ylabel("xGI per 90 (rolling 5)")
    ax.set_ylim(0, 1.2)
    brand.finish(fig, f"{OUT}/preview_xg_trend.png")


def chart_value_scatter():
    rng = np.random.default_rng(11)
    n = 60
    own = np.clip(rng.gamma(2.2, 8, n), 0.5, 70)
    value = np.clip(rng.normal(6.4, 1.5, n) + (70 - own) * 0.012, 2.5, 11)
    fig, ax = brand.new_chart(
        "The market is sleeping on these",
        "Points per £m vs. ownership — top-right is consensus, top-left is edge",
    )
    ax.scatter(own, value, s=42, color=AQUA, alpha=0.55, edgecolors="none")
    hero_idx = np.argsort(value - own * 0.05)[-3:]
    ax.scatter(own[hero_idx], value[hero_idx], s=90, color=LIME, zorder=5)
    for i, name in zip(hero_idx, ["Kudus", "Mbeumo", "Gakpo"]):
        ax.annotate(name, (own[i], value[i]), xytext=(8, 6),
                    textcoords="offset points", color=LIME, fontsize=10.5,
                    fontweight="bold")
    ax.set_xlabel("Ownership %")
    ax.set_ylabel("Points per £m")
    brand.finish(fig, f"{OUT}/preview_value_scatter.png")


if __name__ == "__main__":
    chart_fixture_heatmap()
    chart_xg_trend()
    chart_value_scatter()
