#!/usr/bin/env python3
"""Draw exact, editable vector figures for the temporal certificate paper.

Run from any directory. The only inputs are the mathematical example and
layout constants below. No measured results or generated images are used.
"""
from pathlib import Path
import json
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, PathPatch
from matplotlib.path import Path as MplPath
from PIL import Image

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent / "paper" / "figures"
PAPER.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7.4,
    "mathtext.fontset": "dejavusans",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "axes.unicode_minus": False,
    "savefig.facecolor": "white",
})

INK = "#203047"
MUTED = "#63748A"
PALE = "#E5EAF1"
BLUE = "#355DCA"
BLUE_PALE = "#E4EAFB"
TEAL = "#087F83"
TEAL_PALE = "#DDF2EF"
CORAL = "#CC6238"
CORAL_PALE = "#F9E5DC"
GREY_PALE = "#F1F3F7"


def canvas(width, height):
    fig = plt.figure(figsize=(width, height), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, width), ylim=(0, height))
    ax.set_axis_off()
    return fig, ax


def txt(ax, x, y, s, size=7.5, color=INK, weight="normal", ha="left", va="center", **kw):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                   ha=ha, va=va, linespacing=1.26, **kw)


def line(ax, x1, y1, x2, y2, color=PALE, lw=0.7, **kw):
    return ax.plot([x1, x2], [y1, y2], color=color, lw=lw, **kw)[0]


def arrow(ax, x1, y1, x2, y2, color=MUTED, lw=1.0, rad=0, scale=8):
    patch = FancyArrowPatch((x1, y1), (x2, y2),
                            arrowstyle="-|>", mutation_scale=scale,
                            linewidth=lw, color=color,
                            connectionstyle=f"arc3,rad={rad}",
                            shrinkA=0, shrinkB=0)
    ax.add_patch(patch)
    return patch


def dot(ax, x, y, color, r=.031, opened=False, zorder=4):
    ax.add_patch(Circle((x, y), r, facecolor="white" if opened else color,
                       edgecolor=color, lw=1.15, zorder=zorder))


def interval(ax, x1, x2, y, color, width=6):
    line(ax, x1, y, x2, y, color, width, solid_capstyle="round")
    dot(ax, x1, y, color, .027)
    dot(ax, x2, y, color, .027)


def stage(ax, x, y, number, title, color):
    txt(ax, x, y, number, 7.2, color, "bold")
    txt(ax, x+.26, y, title, 9.0, INK, "bold")
    line(ax, x, y-.135, x+.14, y-.135, color, 2.0)


def finish(fig, name, width, height):
    for suffix in ("pdf", "svg", "png"):
        path = HERE / f"{name}.{suffix}"
        kwargs = {"dpi": 300} if suffix == "png" else {}
        if suffix == "pdf":
            kwargs["metadata"] = {
                "Title": name.replace("_", " "),
                "Author": "Anonymous ACL submission",
                "Subject": "Exact temporal support and context stability",
                "Creator": "Matplotlib; editable source in draw_figures.py",
                "CreationDate": None,
                "ModDate": None,
            }
        fig.savefig(path, **kwargs)
        shutil.copy2(path, PAPER / path.name)
    fig.savefig(HERE / f"{name}_actual_size.png", dpi=144)
    acl_width = 16/2.54 if width > 5 else 7.7/2.54
    with Image.open(HERE / f"{name}.png") as src:
        src.resize((round(acl_width*144), round(height*acl_width/width*144)),
                   Image.Resampling.LANCZOS).save(HERE / f"{name}_acl_size.png")
    plt.close(fig)
    return {"width_inches": width, "height_inches": height,
            "vector_formats": ["pdf", "svg"], "preview_dpi": 144}


def architecture():
    W, H = 7.0, 2.35
    fig, ax = canvas(W, H)
    stage(ax, .06, 2.19, "01", "Read the source", TEAL)
    stage(ax, 2.33, 2.19, "02", "Keep the date range", BLUE)
    stage(ax, 4.72, 2.19, "03", "Certify the context", CORAL)

    # An illustrative source, without the formal notation needed in Figure 2.
    txt(ax, .06, 1.85, "Illustrative source excerpt", 7.2, MUTED)
    line(ax, .07, 1.55, .07, 1.18, TEAL, 2.0)
    txt(ax, .19, 1.54, '“A took office in 2010.”', 8.0, TEAL)
    txt(ax, .19, 1.22, '“B replaced A in 2015.”', 8.0, BLUE)
    txt(ax, .06, .84, "Compile the source witness", 7.2, MUTED)
    for x, name, col in [(.34, "B", BLUE), (1.45, "A", TEAL)]:
        ax.add_patch(Circle((x, .49), .145, facecolor="white", edgecolor=col, lw=1.3))
        txt(ax, x, .49, name, 10.0, col, "bold", ha="center")
    arrow(ax, .52, .49, 1.25, .49, BLUE, 1.3)
    txt(ax, .88, .66, "replaces", 7.1, MUTED, ha="center")
    txt(ax, .06, .14, "A's start precedes the query year.", 7.2, MUTED)
    arrow(ax, 1.90, .49, 2.17, .49, MUTED, .9)

    # Day positions are exact for non-leap year 2015.
    # Jan 1=0, June 1=151, Dec 1=334, Dec 31=364.
    x = lambda day: 2.88 + 1.41*day/364
    jq = x(151)
    jd = x(334)
    txt(ax, 2.33, 1.85, "B can start on any day in 2015.", 7.2, MUTED)
    txt(ax, 2.34, 1.52, "Range", 7.2, MUTED)
    line(ax, x(0), 1.52, x(364), 1.52, BLUE_PALE, 8, solid_capstyle="butt")
    dot(ax, x(0), 1.52, BLUE, .027)
    dot(ax, x(364), 1.52, BLUE, .027)
    txt(ax, x(0), 1.29, "1 Jan", 7.2, MUTED, ha="center")
    txt(ax, x(364), 1.29, "31 Dec", 7.2, MUTED, ha="center")
    txt(ax, jq, 1.68, "1 June", 7.1, CORAL, "bold", ha="center")
    line(ax, jq, .44, jq, 1.59, CORAL, .85, linestyle=(0, (2, 2)), zorder=1)
    txt(ax, 2.34, 1.01, "Jan start", 7.2, MUTED)
    txt(ax, 2.34, .61, "Dec start", 7.2, MUTED)
    line(ax, x(0), 1.01, x(364), 1.01, BLUE, 4.5, solid_capstyle="butt")
    dot(ax, x(0), 1.01, BLUE, .030)
    line(ax, x(0), .61, jd, .61, TEAL, 4.5, solid_capstyle="butt")
    line(ax, jd, .61, x(364), .61, BLUE, 4.5, solid_capstyle="butt")
    dot(ax, jd, .61, BLUE, .034)
    for y, name, col in [(1.01, "B", BLUE), (.61, "A", TEAL)]:
        ax.add_patch(Circle((jq, y), .107, facecolor="white", edgecolor=col, lw=1.1, zorder=5))
        txt(ax, jq, y, name, 8.9, col, "bold", ha="center", zorder=6)
    txt(ax, 3.44, .14, "Both timelines satisfy the source.", 7.2, MUTED, ha="center")
    arrow(ax, 4.43, .95, 4.62, .95, MUTED, .9)

    # One fixed ranking. The overview has fixed fallback eligibility.
    txt(ax, 4.72, 1.85, "Who held office on 1 June 2015?", 7.2, INK, "bold")
    rows = [
        (1, "overview", "fixed", MUTED, GREY_PALE),
        (2, "A's tenure", "", TEAL, TEAL_PALE),
        (3, "B's tenure", "", BLUE, BLUE_PALE),
    ]
    for i, label, tag, col, fill in rows:
        y = 1.52-(i-1)*.28
        ax.add_patch(Rectangle((4.98, y-.105), 1.30, .21, facecolor=fill, edgecolor="none"))
        txt(ax, 4.80, y, str(i), 7.2, MUTED, ha="center")
        txt(ax, 5.04, y, label, 7.2, col)
        if tag:
            txt(ax, 6.21, y, tag, 7.2, col, ha="right")
    line(ax, 6.36, 1.64, 6.36, 1.40, TEAL, 1.05)
    line(ax, 6.31, 1.64, 6.36, 1.64, TEAL, 1.05)
    line(ax, 6.31, 1.40, 6.36, 1.40, TEAL, 1.05)
    txt(ax, 6.48, 1.60, "$k=1$", 7.7, TEAL, "bold")
    txt(ax, 6.48, 1.38, "stable", 7.2, TEAL, "bold")
    txt(ax, 4.74, .65, "$k=2$: the context changes", 7.4, CORAL, "bold")
    txt(ax, 4.74, .38, "Jan start", 7.2, MUTED)
    txt(ax, 5.55, .38, "[overview, B]", 8.0, BLUE, "bold")
    txt(ax, 4.74, .14, "Dec start", 7.2, MUTED)
    txt(ax, 5.55, .14, "[overview, A]", 8.0, TEAL, "bold")
    return finish(fig, "architecture", W, H)


def coverage():
    W, H = 3.35, 1.80
    fig, ax = canvas(W, H)
    txt(ax, .03, 1.65, "ALL QUESTIONS", 7.2, MUTED, "bold")
    txt(ax, 2.21, 1.65, "MODELED ONLY", 7.2, MUTED, "bold")
    # The full bars share a 100% scale. The right bars expand the modeled subset.
    # Stable/changed here describe contexts, not extraction accuracy.
    full_x, full_w, zoom_x, zoom_w, bar_h = .03, 1.88, 2.21, 1.10, .18
    fallback_col = "#B4BFCD"
    unparsed_col = "#E8EBF0"
    rows = [
        ("Template", 2348, 2053, 189, 54, 52, 1.17),
        ("Human", 830, 747, 56, 10, 17, .57),
    ]
    for label, total, fallback, stable, changed, unparsed, y in rows:
        assert total == fallback+stable+changed+unparsed
        modeled = stable+changed
        txt(ax, full_x, y+.245, f"{label} · {total:,}", 7.2, INK, "bold")
        txt(ax, zoom_x+zoom_w, y+.245, str(modeled), 7.2, INK, "bold", ha="right")
        left = full_x
        for count, col in [(fallback, fallback_col), (stable, TEAL), (changed, CORAL), (unparsed, unparsed_col)]:
            width = full_w*count/total
            ax.add_patch(Rectangle((left, y-bar_h/2), width, bar_h, facecolor=col, edgecolor="none"))
            left += width
        txt(ax, full_x+full_w*fallback/total/2, y, f"{fallback:,} fallback", 7.2, INK, ha="center")
        txt(ax, full_x+full_w, y-.235, f"{unparsed} unparsed", 7.2, MUTED, ha="right")
        a = full_x+full_w*fallback/total
        b = full_x+full_w*(fallback+modeled)/total
        # Thin connectors link the exact segment to its conditional display.
        line(ax, a, y+bar_h/2+.005, zoom_x, y+bar_h/2+.055, PALE, .75)
        line(ax, b, y-bar_h/2-.005, zoom_x, y-bar_h/2-.055, PALE, .75)
        sw = zoom_w*stable/modeled
        ax.add_patch(Rectangle((zoom_x, y-bar_h/2), sw, bar_h, facecolor=TEAL, edgecolor="none"))
        ax.add_patch(Rectangle((zoom_x+sw, y-bar_h/2), zoom_w-sw, bar_h, facecolor=CORAL, edgecolor="none"))
        txt(ax, zoom_x+sw/2, y, str(stable), 7.2, "white", "bold", ha="center")
        txt(ax, zoom_x+sw+(zoom_w-sw)/2, y, str(changed), 7.2, "white", "bold", ha="center")
    # Every category has a text label, independent of its color.
    for x, label, col in [(.03, "Fallback", fallback_col), (.90, "Stable", TEAL), (1.67, "Unstable", CORAL), (2.57, "Unparsed", unparsed_col)]:
        ax.add_patch(Rectangle((x, .084), .090, .090, facecolor=col, edgecolor="none"))
        txt(ax, x+.125, .129, label, 7.2, MUTED)
    return finish(fig, "coverage", W, H)


def two_witnesses():
    W, H = 3.35, 2.65
    fig, ax = canvas(W, H)
    txt(ax, .04, 2.50, "EVENT DATES", 7.2, MUTED, "bold")
    txt(ax, 3.30, 2.50, r"Accepted pairs: $d\to c,\ e\to c$", 7.2, MUTED, ha="right")
    x = lambda t: .53 + .445*t
    for lab, left, right, y, col in [
        ("c", 0, 2, 2.17, INK),
        ("d", 1, 4, 1.86, TEAL),
        ("e", 3, 5, 1.55, BLUE),
    ]:
        txt(ax, .15, y, "$"+lab+"$", 9.4, col, "bold")
        line(ax, x(0), y, x(6), y, PALE, .65)
        interval(ax, x(left), x(right), y, col, width=5.5)
    txt(ax, x(1), 1.99, r"$r_c=1$", 7.4, TEAL, ha="center")
    txt(ax, x(5), 1.68, r"$p_c=5$", 7.4, BLUE, ha="center")
    # The supplying lower and upper bounds map to exact support cutoffs.
    line(ax, x(1), 1.82, x(1), .68, TEAL, .75, linestyle=(0, (2, 2)), zorder=1)
    line(ax, x(5), 1.51, x(5), .94, BLUE, .75, linestyle=(0, (2, 2)), zorder=1)
    line(ax, x(0), 1.29, x(6), 1.29, MUTED, .65)
    for t in range(7):
        line(ax, x(t), 1.29, x(t), 1.25, MUTED, .65)
        txt(ax, x(t), 1.14, str(t), 7.2, MUTED, ha="center")

    txt(ax, .04, .94, "$P$", 8.7, BLUE, "bold")
    txt(ax, .04, .68, "$H$", 8.7, TEAL, "bold")
    for y, cutoff, col in [(.94, 5, BLUE), (.68, 1, TEAL)]:
        line(ax, x(0), y, x(6), y, PALE, 7.2, solid_capstyle="butt")
        line(ax, x(0), y, x(cutoff), y, col, 7.2, solid_capstyle="butt")
        dot(ax, x(0), y, col, .031)
        dot(ax, x(cutoff), y, col, .039, opened=True)
    txt(ax, 1.81, .45, r"Windows $[a,6]$: vary the start $a$", 7.2, MUTED, ha="center")

    # The bottom row records the two distinct one-witness errors.
    line(ax, .04, .32, 3.30, .32, PALE, .65)
    txt(ax, .05, .18, r"Only $d$: wrongly possible at 5", 7.2, BLUE)
    txt(ax, 3.29, .18, r"Only $e$: wrongly guaranteed at 2", 7.2, TEAL, ha="right")
    return finish(fig, "two_witnesses", W, H)


if __name__ == "__main__":
    info = {"architecture": architecture(), "two_witnesses": two_witnesses(), "coverage": coverage()}
    (HERE / "figure_manifest.json").write_text(json.dumps(info, indent=2)+"\n")
    print(json.dumps(info, indent=2))
