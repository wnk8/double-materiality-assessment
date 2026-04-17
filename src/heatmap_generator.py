"""
ESRS Heatmap Generator — topic-level materiality overview.

Rows: 7 ESRS topics
Columns:
    Auswirkungsscore  — max impact score across all IROs in the topic
    Finanzscore       — max financial score across all IROs in the topic
    Doppelt wesentlich — 1.0 (Ja) or 0.0 (Nein)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

# Canonical topic order and German display names
TOPIC_ORDER = ["E1", "E2", "E3", "S1", "S2", "G1", "G2"]
TOPIC_LABELS = {
    "E1": "E1 — Klimawandel",
    "E2": "E2 — Umweltverschmutzung",
    "E3": "E3 — Wasser & Meeresressourcen",
    "S1": "S1 — Eigene Belegschaft",
    "S2": "S2 — Arbeitskräfte in der Lieferkette",
    "G1": "G1 — Unternehmensführung",
    "G2": "G2 — Unternehmenskultur & Antikorruption",
}
COLUMN_LABELS = ["Auswirkungsscore", "Finanzscore", "Doppelt wesentlich"]


def generate_heatmap(topic_aggregates: dict, output_path: str) -> None:
    """
    Generate the ESRS heatmap and save to output_path.

    Args:
        topic_aggregates: Output of scoring_engine.aggregate_by_topic().
        output_path: Destination file path (.png).
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Build data matrix
    data = []
    annot = []
    row_labels = []

    for topic_code in TOPIC_ORDER:
        agg = topic_aggregates.get(topic_code, {
            "max_impact": 0.0, "max_financial": 0.0, "doubly_material": False
        })
        impact = agg["max_impact"]
        financial = agg["max_financial"]
        doubly = 1.0 if agg["doubly_material"] else 0.0

        data.append([impact, financial, doubly])
        annot.append([
            f"{impact:.1f}",
            f"{financial:.1f}",
            "Ja" if agg["doubly_material"] else "Nein",
        ])
        row_labels.append(TOPIC_LABELS.get(topic_code, topic_code))

    data_array = np.array(data, dtype=float)

    fig, ax = plt.subplots(figsize=(8, 5))

    if HAS_SEABORN:
        sns.heatmap(
            data_array,
            ax=ax,
            cmap="YlGn",
            vmin=0,
            vmax=5,
            annot=np.array(annot),
            fmt="",
            linewidths=0.5,
            linecolor="#CCCCCC",
            cbar_kws={"label": "Score (0–5)", "shrink": 0.7},
            xticklabels=COLUMN_LABELS,
            yticklabels=row_labels,
        )
    else:
        # Fallback: plain matplotlib imshow
        im = ax.imshow(data_array, cmap="YlGn", vmin=0, vmax=5, aspect="auto")
        ax.set_xticks(range(len(COLUMN_LABELS)))
        ax.set_xticklabels(COLUMN_LABELS)
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels)
        fig.colorbar(im, ax=ax, label="Score (0–5)", shrink=0.7)

        for i in range(data_array.shape[0]):
            for j in range(data_array.shape[1]):
                ax.text(j, i, annot[i][j],
                        ha="center", va="center", fontsize=9, color="#333333")

    ax.set_title(
        "ESRS-Wesentlichkeitsübersicht",
        fontsize=13, fontweight="bold", pad=14, color="#1F4E79"
    )
    ax.tick_params(axis="x", labelsize=9, rotation=0)
    ax.tick_params(axis="y", labelsize=8.5, rotation=0)

    plt.tight_layout()
    try:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
    except OSError as e:
        raise OSError(f"Could not save heatmap to '{output_path}': {e}") from e
    finally:
        plt.close(fig)

    print(f"[OK] ESRS-Heatmap gespeichert: {output_path}")
