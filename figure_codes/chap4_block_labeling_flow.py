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
from thesis_style import FONT, TEXT_WIDTH_IN, savefig_text_width

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap4-block-labeling-flow.pdf"


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 2.05))
    ax.set_xlim(-0.05, 14.6)
    ax.set_ylim(0.55, 4.45)
    ax.axis("off")

    y = 2.5
    fs = FONT["note"] - 1
    gap = 0.58  # 框间水平箭头间隙

    # 压矮：分支上下靠拢；中间框略降高、加宽保文字
    w1, w2, w3, wd, wr = 1.9, 2.7, 3.15, 2.05, 1.7
    h_box, h_mid, h_dec = 0.95, 1.22, 1.55

    c1 = 1.1
    c2 = c1 + w1 / 2 + gap + w2 / 2
    c3 = c2 + w2 / 2 + gap + w3 / 2
    cd = c3 + w3 / 2 + gap + wd / 2
    branch_run = 0.95
    cr = cd + wd / 2 + branch_run + wr / 2

    process(ax, (c1, y), w1, h_box, "物理 / 逻辑块\nBLOCK", fontsize=fs)
    arrow(ax, (c1 + w1 / 2, y), (c2 - w2 / 2, y))

    process(
        ax, (c2, y), w2, h_mid,
        "代表性 FBC\n$P_{99}$（BestRead）", fontsize=fs,
    )
    arrow(ax, (c2 + w2 / 2, y), (c3 - w3 / 2, y))

    process(
        ax, (c3, y), w3, h_mid,
        "对照 FBC 门限 $=151$\n推导 LIFESPAN", fontsize=fs,
    )
    arrow(ax, (c3 + w3 / 2, y), (cd - wd / 2, y))

    decision(ax, (cd, y), wd, h_dec, "LIFESPAN\n$=10000$？", fontsize=fs)

    y_yes, y_no = 3.45, 1.55
    routed_arrow(ax, [(cd, y + h_dec / 2), (cd, y_yes), (cr - wr / 2, y_yes)])
    routed_arrow(ax, [(cd, y - h_dec / 2), (cd, y_no), (cr - wr / 2, y_no)])
    edge_label(ax, ((cd + cr - wr / 2) / 2, y_yes + 0.18), "是", fontsize=fs)
    edge_label(ax, ((cd + cr - wr / 2) / 2, y_no - 0.18), "否", fontsize=fs)

    process(ax, (cr, y_yes), wr, h_box, "强块\nLabel $=0$", fontsize=fs)
    process(ax, (cr, y_no), wr, h_box, "弱块\nLabel $=1$", fontsize=fs)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_pdf, pad_inches=0.03)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
