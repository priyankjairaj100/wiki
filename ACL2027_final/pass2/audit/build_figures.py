"""Editable vector architecture and exact illustrative temporal worlds."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                     "pdf.fonttype": 42, "svg.fonttype": "none"})
NAVY, TEAL, GRAY, AMBER = "#16364D", "#087E83", "#647580", "#AC5C24"
fig, ax = plt.subplots(figsize=(7.1, 2.72))
ax.set(xlim=(0, 10), ylim=(0, 4)); ax.axis("off")

def box(x, y, w, h, title, body, color=NAVY):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.07,rounding_size=0.05",
        lw=.9, ec=color, fc="#F5F8FA"))
    ax.text(x+.12, y+h-.15, title, color=color, fontsize=8.2,
            weight="bold", va="top")
    ax.text(x+.12, y+h-.52, body, color=NAVY, fontsize=7.6,
            va="top", linespacing=1.5)

def arrow(start, end, color=GRAY):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                 mutation_scale=9, lw=.9, color=color))

ax.text(.12, 3.85, "SOURCE EVIDENCE", fontsize=6.8, color=GRAY, weight="bold")
ax.text(3.14, 3.85, "COMPILE ONCE", fontsize=6.8, color=GRAY, weight="bold")
ax.text(6.77, 3.85, "EACH QUERY", fontsize=6.8, color=GRAY, weight="bold")
box(.12, 2.38, 2.48, 1.22, "1  Preserve date precision",
    "Claim + source span\nEarliest / latest possible start")
box(3.14, 2.38, 2.98, 1.22, "2  Compile two witnesses",
    "Fixed pair decisions\nTwo boundaries + source witnesses", TEAL)
box(6.77, 2.38, 3.03, 1.22, "3  Test the requested period",
    "Possible / guaranteed support\nFilter fixed ranks; apply budget")
arrow((2.71, 2.99), (3.04, 2.99))
arrow((6.23, 2.99), (6.67, 2.99))

ax.plot([.1, 9.9], [2.09, 2.09], color="#D7E0E5", lw=.7)
ax.text(.12, 1.84, "WHY A RANGE IS DIFFERENT", color=NAVY,
        fontsize=7.2, weight="bold")
ax.text(.12, 1.46, "Claim c starts at an unknown time in [0, 10].",
        color=NAVY, fontsize=7.5)
ax.text(.12, 1.10, "A conflicting claim d starts at time 5.", color=NAVY, fontsize=7.5)
ax.text(.12, .63, "Every timeline supports c somewhere in [0, 10].",
        color=TEAL, weight="bold", fontsize=7.5)
ax.text(.12, .28, "No single time supports c in every timeline.",
        color=GRAY, fontsize=7.5)

left, scale = 6.40, .275
tx = lambda t: left + t * scale
ax.axvspan(tx(0), tx(10), ymin=.095, ymax=.472, facecolor="#E9F3F4", zorder=-3)
for time in [0, 5, 10]:
    ax.plot([tx(time)]*2, [.38, 1.76], color="#CADADD", lw=.65, zorder=-1)
    ax.text(tx(time), .18, str(time), ha="center", color=GRAY, fontsize=7)
ax.text(tx(5), 1.90, "Question period: [0, 10]", ha="center", color=GRAY, fontsize=7.2)
for y, start, stop, label, color in [
    (1.38, 2, 5, "c starts at 2", AMBER),
    (.77, 8, 12, "c starts at 8", TEAL)]:
    ax.text(6.18, y, label, ha="right", va="center", fontsize=7.2, color=NAVY)
    ax.plot([tx(start), tx(stop)], [y]*2, color=color, lw=2.6, solid_capstyle="butt")
    ax.plot(tx(start), y, "o", ms=3.4, color=color)
    if stop == 5:
        ax.plot(tx(stop), y, "o", ms=3.4, mfc="white", mec=color)
    else:
        arrow((tx(stop)-.03, y), (tx(stop)+.09, y), color)
fig.subplots_adjust(0, 0, 1, 1)
for extension in ("pdf", "svg", "png"):
    fig.savefig(OUT / f"architecture.{extension}", dpi=240)
plt.close(fig)
