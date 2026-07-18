"""第四章：块寿命标签构造流程（黑白印刷版）。

生成 figure/generated/chap4-block-labeling-flow.pdf。

用法（项目根目录）:
    python3 figure_codes/chap4_block_labeling_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from flowchart_style import (
    apply_flowchart_rc,
    arrow,
    decision,
    edge_label,
    process,
    routed_arrow,
)
from thesis_style import FONT

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap4-block-labeling-flow.pdf"

def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(8.6, 2.8))
    ax.set_xlim(0.0, 13.9)
    ax.set_ylim(0.2, 4.8)
    ax.axis("off")

    y = 2.5
    fs = FONT["label"]
    process(ax, (1.5, y), 2.5, 1.0, "物理 / 逻辑块\nBLOCK", fontsize=fs)
    arrow(ax, (2.75, y), (2.9, y))

    process(
        ax, (4.25, y), 2.7, 1.2,
        "代表性 FBC\n$P_{99}$（BestRead）", fontsize=fs,
    )
    arrow(ax, (5.6, y), (5.75, y))

    process(
        ax, (7.4, y), 3.3, 1.2,
        "对照 FBC 门限 $=151$\n推导 LIFESPAN", fontsize=fs,
    )
    arrow(ax, (9.05, y), (9.15, y))

    decision(ax, (10.4, y), 2.5, 1.8, "LIFESPAN\n$=10000$？", fontsize=fs)

    routed_arrow(ax, [(10.4, 3.4), (10.4, 3.75), (11.8, 3.75)])
    routed_arrow(ax, [(10.4, 1.6), (10.4, 1.25), (11.8, 1.25)])
    edge_label(ax, (11.1, 3.97), "是")
    edge_label(ax, (11.1, 1.03), "否")

    process(ax, (12.8, 3.75), 2.0, 1.0, "强块\nLabel $=0$", fontsize=fs)
    process(ax, (12.8, 1.25), 2.0, 1.0, "弱块\nLabel $=1$", fontsize=fs)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
