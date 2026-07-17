"""第四章：LP/MP/UP 分层建模 + 投票融合（黑白印刷版）。

生成 figure/chap4-ensemble-voting-flow.pdf。

用法（项目根目录）:
    python3 figure_codes/chap4_ensemble_voting_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from flowchart_style import apply_flowchart_rc, arrow, process

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap4-ensemble-voting-flow.pdf"

def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(7.6, 3.5))
    ax.set_xlim(0.1, 11.4)
    ax.set_ylim(0.2, 5.8)
    ax.axis("off")

    process(
        ax, (1.35, 3.0), 2.1, 1.4,
        "早期 PE 档位\nFBC 特征$\\mathbf{x}_i$", fontsize=9.3,
    )

    models = [
        (4.3, 4.7, "LightGBM\nUP"),
        (4.3, 3.0, "LightGBM\nMP"),
        (4.3, 1.3, "LightGBM\nLP"),
    ]
    for x, y, t in models:
        process(ax, (x, y), 1.9, 1.0, t, fontsize=9.3)

    process(
        ax, (7.25, 3.0), 2.0, 1.3,
        "多数投票\n（3 种页类型）", fontsize=9.3,
    )
    process(
        ax, (10.15, 3.0), 2.1, 1.3,
        "块级标签\n强块 / 弱块", fontsize=9.3,
    )

    for (_, y, _), vote_y in zip(models, (3.5, 3.0, 2.5)):
        arrow(ax, (2.4, 3.0), (3.35, y))
        arrow(ax, (5.25, y), (6.25, vote_y))
    arrow(ax, (8.25, 3.0), (9.1, 3.0))

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
