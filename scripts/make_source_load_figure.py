"""Plot archived AC responses for S-T and S-L, without model or solver calls.

Run from any directory:
    python scripts/make_source_load_figure.py

Input values and original evidence hashes are in data/source_load_plot_data.json.
The CSV-equivalent numeric values remain at archived precision in that JSON.
Dependencies: matplotlib and numpy. Output: vector PDF and 300-dpi PNG.
"""
from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/source_load_plot_data.json").read_text(encoding="utf-8"))
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
CASES = DATA["cases"]
IDS = ["G1", "G2", "BAL"]
COLORS = ["#355F7D", "#B77643"]
INK = "#28333A"

# Check that plotted changes are exactly the archived actual-minus-baseline
# quantities to numerical roundoff. This checks transcription, not the solver.
for case in CASES:
    assert case["all_requirements_passed"] is True
    assert [row["id"] for row in case["sources"]] == IDS
    for row in case["sources"]:
        for field in ["P_MW", "Q_Mvar"]:
            assert math.isclose(
                row[field + "_actual"] - row[field + "_baseline"],
                row[field + "_delta"],
                rel_tol=1e-10, abs_tol=1e-12,
            )
    for field, unit in [("P", "MW"), ("Q", "Mvar")]:
        assert math.isclose(
            sum(row[f"delta_{field}_{unit}"] for row in case["selected_loads"]),
            case[f"selected_load_total_delta_{field}_{unit}"],
            rel_tol=1e-10, abs_tol=1e-12,
        )

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5,
    "axes.labelsize": 9, "axes.titlesize": 9.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8.5,
    "legend.fontsize": 8.5, "axes.linewidth": .65,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.facecolor": "white", "figure.facecolor": "white",
})


def label(value):
    """Scientific notation preserves the tiny nonzero responses near zero."""
    if value == 0:
        return "0"
    if abs(value) < .001:
        exp = int(math.floor(math.log10(abs(value))))
        mantissa = value / 10**exp
        return rf"${mantissa:+.2f}\times10^{{{exp}}}$"
    return f"{value:+.3f}"


fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.55))
ys = np.arange(len(IDS))
offsets = [-.16, .16]
settings = [
    ("P_MW_delta", r"Actual $\Delta P$ (MW)", "(a) Active-power response", (-17.5, 17.5), [-12, -6, 0, 6, 12]),
    ("Q_Mvar_delta", r"Actual $\Delta Q$ (Mvar)", "(b) Reactive-power response", (-.7, 1.85), [-.5, 0, .5, 1, 1.5]),
]
for ax, (field, xlabel, title, limits, ticks) in zip(axes, settings):
    for i, case in enumerate(CASES):
        values = [r[field] for r in case["sources"]]
        y = ys + offsets[i]
        ax.barh(y, values, height=.25, color=COLORS[i], edgecolor="white", linewidth=.4, zorder=3)
        # Endpoint dots keep a response visible when it is too small to form a
        # perceptible bar at the common linear scale; no bar length is inflated.
        ax.plot(values, y, "o", color=COLORS[i], markersize=2.8, zorder=4)
        for yy, value in zip(y, values):
            positive = value >= 0
            ax.annotate(label(value), (value, yy), xytext=(4 if positive else -4, 0),
                        textcoords="offset points", va="center",
                        ha="left" if positive else "right", fontsize=8, color=INK)
    ax.axvline(0, color=INK, linewidth=.7, zorder=2)
    ax.set_xlim(*limits)
    ax.set_xticks(ticks)
    ax.set_ylim(2.5, -.5)
    ax.set_yticks(ys, ["G1", "G2", "BAL"])
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", pad=10)
    ax.tick_params(direction="out", length=3, width=.65)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#D8DDDF", linewidth=.45)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)

fig.legend(handles=[Patch(facecolor=COLORS[0], label="S-T: joint generation/load adjustment"),
                    Patch(facecolor=COLORS[1], label="S-L: generation redispatch")],
           loc="upper center", bbox_to_anchor=(.51, 1.005), ncol=2,
           frameon=False, columnspacing=2, handlelength=1.5)

# Loads are annotated separately because their plotted quantities are inputs,
# whereas G1/G2/BAL above are actual output readings.
fig.text(.09, .105,
         r"S-T selected load totals: $\Delta P=+1.526\times10^{-5}$ MW; $\Delta Q=-0.509617$ Mvar.",
         fontsize=8, va="center", color=INK)
fig.text(.09, .045,
         "S-L: all four selected load P/Q inputs remain unchanged. Generator controls are retained in both cases.",
         fontsize=8, va="center", color=INK)
fig.subplots_adjust(left=.09, right=.985, top=.79, bottom=.28, wspace=.26)
for suffix in ["pdf", "png"]:
    kwargs = {"dpi": 300} if suffix == "png" else {}
    fig.savefig(OUT / f"fig4_source_load_response.{suffix}",
                bbox_inches="tight", pad_inches=.06, **kwargs)
plt.close(fig)
print("Wrote fig4_source_load_response.pdf and .png from archived values only.")
