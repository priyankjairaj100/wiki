"""Draw an editable vector architecture figure at ACL two-column width."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, PathPatch
from matplotlib.path import Path as MplPath

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "paper/figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})
INK, TEAL, AMBER = "#20334a", "#087b80", "#97630a"
fig, ax = plt.subplots(figsize=(7.0, 2.14))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax.set_xlim(0, 7)
ax.set_ylim(0, 2.14)
ax.axis("off")


def txt(x, y, s, size=8, color=INK, weight="normal", ha="center", va="center"):
    ax.text(x, y, s, fontsize=size, color=color, weight=weight, ha=ha, va=va,
            linespacing=1.2)


def box(x, width, title, lines, color=INK):
    y, height = 1.35, .73
    ax.add_patch(Rectangle((x, y), width, height, lw=.8, ec=color, fc="white"))
    ax.add_patch(Rectangle((x, y+height-.055), width, .055, lw=0, fc=color))
    txt(x+width/2, 1.90, title, size=8.25, weight="bold", color=color)
    txt(x+width/2, 1.58, lines, size=7.5)


nodes = [
    (.04, 1.10, "Source excerpts", "date phrases\nsource spans", INK),
    (1.30, 1.31, "Lifecycle adapter", "start and end bounds\nexplicit succession\nunparsed text", INK),
    (2.77, 1.30, "Temporal compiler", "two witness records\npoint and period tests", TEAL),
    (4.23, 1.48, "Context certificate", "query window + ranking\nsame selected excerpts?", TEAL),
    (5.87, 1.09, "Answer model", "original evidence\nanswer", INK),
]
for node in nodes:
    box(*node)
for a, b in zip(nodes, nodes[1:]):
    ax.add_patch(FancyArrowPatch((a[0]+a[1]+.016, 1.72), (b[0]-.016, 1.72),
        arrowstyle="-|>", mutation_scale=8, linewidth=.9, color=INK))

# Unparsed clauses stay available. The adapter does not delete whole paragraphs.
verts = [(1.92, 1.35), (1.92, 1.16), (4.98, 1.16), (4.98, 1.35)]
path = MplPath(verts, [MplPath.MOVETO, MplPath.LINETO, MplPath.LINETO, MplPath.LINETO])
ax.add_patch(FancyArrowPatch(path=path, arrowstyle="-|>", mutation_scale=7,
                            lw=.8, linestyle=(0, (3, 2)), color=INK))
ax.text(3.45, 1.17, "  unparsed text joins ranked selection  ", ha="center", va="center",
        fontsize=7.2, color=INK, bbox=dict(facecolor="white", edgecolor="none", pad=.5))

# A logical illustration, not a benchmark example or a measured ranking.
ax.add_patch(Rectangle((.04, .055), 6.92, .98, fc="#f4f7f9", ec="#b6c2cd", lw=.65))
txt(.18, .88, "Uncertainty matters only when it reaches the context", size=8.3,
    weight="bold", ha="left")
txt(.18, .61, "Ranked claims", size=7.5, ha="left")
txt(.18, .34, "c  >  d  >  e", size=9.4, weight="bold", ha="left")

ax.plot([1.46, 1.46], [.19, .77], color="#b6c2cd", lw=.6)
txt(1.62, .61, "Possible:   {c, d, e}", size=8, ha="left")
txt(1.62, .34, "Guaranteed:   {c, e}", size=8, ha="left", color=TEAL)
ax.plot([3.46, 3.46], [.19, .77], color="#b6c2cd", lw=.6)

txt(3.66, .63, "Budget 1: stable", size=8.1, color=TEAL, weight="bold", ha="left")
txt(3.66, .35, "Every timeline returns [c]", size=7.5, ha="left")
ax.plot([5.31, 5.31], [.19, .77], color="#b6c2cd", lw=.6)
txt(5.48, .63, "Budget 2: unstable", size=8.1, color=AMBER, weight="bold", ha="left")
txt(5.48, .36, "Timeline 1: [c, d]\nTimeline 2: [c, e]", size=7.5, ha="left")

for extension in ["pdf", "svg", "png"]:
    fig.savefig(OUT / f"architecture.{extension}", dpi=250, facecolor="white")
plt.close(fig)
print(OUT / "architecture.pdf")
