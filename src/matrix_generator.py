"""
Materiality Matrix Generator — scatter plot of Impact vs Financial scores.

Quadrants (threshold at 3.0 on both axes):
    Bottom-left  (both < 3):   grey   — Nicht wesentlich
    Top-left     (impact ≥ 3): orange — Auswirkungswesentlich
    Bottom-right (fin ≥ 3):    orange — Finanziell wesentlich
    Top-right    (both ≥ 3):   red    — Doppelt wesentlich
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

THRESHOLD = 3.0

TYPE_COLORS = {
    "Impact": "#2196F3",       # blue
    "Risk": "#FF9800",          # orange
    "Opportunity": "#4CAF50",   # green
}

QUADRANT_COLORS = {
    "none":      "#E0E0E0",  # grey
    "impact":    "#FFE0B2",  # light orange
    "financial": "#FFE0B2",  # light orange
    "both":      "#FFCDD2",  # light red
}


def generate_matrix(scored_iros: list[dict], output_path: str) -> None:
    """
    Generate the materiality matrix scatter plot and save to output_path.

    Args:
        scored_iros: List of scored IRO dicts (output of scoring_engine.score_iros).
        output_path: Destination file path (.png).
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))

    # ── Quadrant fills ───────────────────────────────────────────────────────
    ax.axhspan(1, THRESHOLD, xmin=0, xmax=(THRESHOLD - 1) / 4,
               facecolor=QUADRANT_COLORS["none"], alpha=0.5, zorder=0)
    ax.axhspan(THRESHOLD, 5, xmin=0, xmax=(THRESHOLD - 1) / 4,
               facecolor=QUADRANT_COLORS["impact"], alpha=0.5, zorder=0)
    ax.axhspan(1, THRESHOLD, xmin=(THRESHOLD - 1) / 4, xmax=1,
               facecolor=QUADRANT_COLORS["financial"], alpha=0.5, zorder=0)
    ax.axhspan(THRESHOLD, 5, xmin=(THRESHOLD - 1) / 4, xmax=1,
               facecolor=QUADRANT_COLORS["both"], alpha=0.5, zorder=0)

    # ── Threshold lines ──────────────────────────────────────────────────────
    ax.axhline(y=THRESHOLD, color="#B71C1C", linewidth=1.2,
               linestyle="--", alpha=0.7, zorder=1)
    ax.axvline(x=THRESHOLD, color="#B71C1C", linewidth=1.2,
               linestyle="--", alpha=0.7, zorder=1)

    # ── Quadrant labels ──────────────────────────────────────────────────────
    quadrant_labels = [
        (1.15, 4.7, "Auswirkungswesentlich"),
        (3.15, 4.7, "Doppelt wesentlich"),
        (1.15, 1.15, "Nicht wesentlich"),
        (3.15, 1.15, "Finanziell wesentlich"),
    ]
    for x, y, label in quadrant_labels:
        ax.text(x, y, label, fontsize=7.5, color="#555555",
                alpha=0.8, style="italic", zorder=2)

    # ── Scatter points ───────────────────────────────────────────────────────
    plotted_ids: dict[tuple, list[str]] = {}  # (x,y) → [iro_id, ...]

    for iro in scored_iros:
        x = iro["financial_score"]
        y = iro["impact_score"]
        color = TYPE_COLORS.get(iro["iro_type"], "#9C27B0")

        ax.scatter(x, y, color=color, s=90, zorder=3,
                   edgecolors="white", linewidths=0.8)

        key = (round(x, 1), round(y, 1))
        plotted_ids.setdefault(key, []).append(iro["iro_id"])

    # Labels — stagger duplicates to avoid overlap
    for (x, y), ids in plotted_ids.items():
        for offset, iro_id in enumerate(ids):
            ax.annotate(
                iro_id,
                xy=(x, y),
                xytext=(6 + offset * 2, 4 + offset * 6),
                textcoords="offset points",
                fontsize=7,
                color="#333333",
                zorder=4,
            )

    # ── Axes & formatting ────────────────────────────────────────────────────
    ax.set_xlim(1, 5)
    ax.set_ylim(1, 5)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Finanzielle Wesentlichkeit (Score)", fontsize=11, labelpad=10)
    ax.set_ylabel("Auswirkungswesentlichkeit (Score)", fontsize=11, labelpad=10)
    ax.set_title(
        "Doppelte Wesentlichkeitsmatrix",
        fontsize=14, fontweight="bold", pad=16, color="#1F4E79"
    )
    ax.tick_params(labelsize=9)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("#FFFFFF")

    for spine in ax.spines.values():
        spine.set_edgecolor("#CCCCCC")

    ax.grid(True, linestyle=":", linewidth=0.5, color="#CCCCCC", alpha=0.7)

    # ── Legend ───────────────────────────────────────────────────────────────
    legend_patches = [
        mpatches.Patch(color=color, label=label)
        for label, color in [
            ("Impact", TYPE_COLORS["Impact"]),
            ("Risk", TYPE_COLORS["Risk"]),
            ("Opportunity", TYPE_COLORS["Opportunity"]),
        ]
    ]
    ax.legend(
        handles=legend_patches,
        title="IRO-Typ",
        title_fontsize=8,
        fontsize=8,
        loc="lower right",
        framealpha=0.9,
    )

    plt.tight_layout()
    try:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
    except OSError as e:
        raise OSError(f"Could not save matrix to '{output_path}': {e}") from e
    finally:
        plt.close(fig)

    print(f"[OK] Wesentlichkeitsmatrix gespeichert: {output_path}")
