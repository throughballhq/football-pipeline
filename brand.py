"""The Throughball — brand module for all pipeline charts.

Palette (Ondrej, 2. 8. 2026):
    INK   #233838  dark teal   -> canvas background (dark-mode charts)
    AQUA  #A4DCDB  light aqua  -> context series, secondary text, grid accents
    LIME  #A9FF46  signal lime -> THE highlight. One story per chart, in lime.
    plus white / near-black for text.

Typography: Fraunces (OFL). Optical sizes used on purpose:
    Fraunces 144pt Bold  -> titles (display cut, maximum character)
    Fraunces 9pt Regular/SemiBold -> labels, ticks, numbers (text cut,
                                     designed to stay readable when small)

Usage:
    import brand
    brand.setup()                     # fonts + rcParams, call once
    fig, ax = brand.new_chart("Title", "subtitle")
    ... plot using brand.INK/AQUA/LIME ...
    brand.finish(fig, "out.png")      # watermark + save
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

# ----------------------------------------------------------------- palette

INK = "#233838"
AQUA = "#A4DCDB"
LIME = "#A9FF46"
WHITE = "#FFFFFF"

BG = INK
GRID = "#33504F"          # ink lightened — subtle gridlines
TEXT = WHITE
TEXT_MUTED = AQUA
CONTEXT = "#6FA3A2"       # desaturated aqua — non-highlighted series

WATERMARK = "thethroughball.com"

FONT_DIR = os.environ.get("BRAND_FONT_DIR", os.path.join(os.path.dirname(__file__), "fonts"))

TITLE_FONT = "Fraunces 144pt"
TEXT_FONT = "Fraunces 9pt"

_setup_done = False


def setup():
    """Register fonts and set global chart style. Call once per process."""
    global _setup_done
    if _setup_done:
        return
    if os.path.isdir(FONT_DIR):
        for f in os.listdir(FONT_DIR):
            if f.lower().endswith((".ttf", ".otf")):
                fm.fontManager.addfont(os.path.join(FONT_DIR, f))
    available = {f.name for f in fm.fontManager.ttflist}
    text_font = TEXT_FONT if TEXT_FONT in available else "DejaVu Sans"

    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "savefig.facecolor": BG,
            "font.family": text_font,
            "text.color": TEXT,
            "axes.edgecolor": GRID,
            "axes.labelcolor": TEXT_MUTED,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "grid.alpha": 0.6,
            "xtick.color": TEXT_MUTED,
            "ytick.color": TEXT_MUTED,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 160,
        }
    )
    _setup_done = True


SIZES = {
    "std": ((10, 6.25), 0.76),     # default, ~16:10
    "wide": ((12.8, 7.2), 0.77),   # 16:9 — X/Twitter timeline
    "square": ((8.5, 8.5), 0.81),  # 1:1 — link cards, IG
}


def new_chart(title: str, subtitle: str = "", size: str = "std", figsize=None):
    """Figure with branded title block. size: 'std' | 'wide' | 'square'."""
    setup()
    preset, axes_top = SIZES.get(size, SIZES["std"])
    fig, ax = plt.subplots(figsize=figsize or preset)
    fig.subplots_adjust(top=axes_top, left=0.09, right=0.96, bottom=0.14)
    fig.text(0.05, 0.955, title, fontfamily=_family(TITLE_FONT),
             fontweight="bold", fontsize=21, color=TEXT, va="top")
    if subtitle:
        fig.text(0.05, 0.885, subtitle, fontsize=10.5, color=TEXT_MUTED, va="top")
    return fig, ax


def finish(fig, path: str):
    """Watermark + save. Every published chart goes through this."""
    fig.text(0.96, 0.03, WATERMARK, fontsize=9.5, color=AQUA,
             alpha=0.75, ha="right", fontweight="bold")
    fig.savefig(path, bbox_inches=None)
    plt.close(fig)
    print(f"chart saved: {path}")


def difficulty_cmap() -> ListedColormap:
    """5-step fixture difficulty scale: 1 easy (light aqua) -> 5 hard (deep ink).

    Deliberately neutral (no lime): the scale describes, lime points.
    Lime stays reserved for highlighting the story — e.g. via
    highlight_cell(ax, col, row) drawing a lime frame around the cells
    that ARE the point of the chart."""
    blend = LinearSegmentedColormap.from_list("tb_diff", ["#C9E8E7", AQUA, "#5F8B8A", "#33504F", "#0F1D1D"])
    return ListedColormap([blend(x) for x in (0.0, 0.25, 0.5, 0.75, 1.0)])


def highlight_cell(ax, col: int, row: int, lw: float = 2.6):
    """Draw a lime frame around one heatmap cell — the story marker."""
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((col - 0.5, row - 0.5), 1, 1, fill=False,
                           edgecolor=LIME, linewidth=lw, zorder=6))


def _family(name: str) -> str:
    available = {f.name for f in fm.fontManager.ttflist}
    return name if name in available else "DejaVu Sans"
