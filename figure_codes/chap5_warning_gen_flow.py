"""第五章：预警生成流程（黑白印刷版）。

生成 figure/generated/chap5-warning-gen-flow.pdf。

用法（项目根目录）:
    python3 figure_codes/chap5_warning_gen_flow.py
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
    terminator,
)
from thesis_style import FONT

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap5-warning-gen-flow.pdf"


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(10.2, 1.95))
    ax.set_xlim(0, 11.5)
    # 紧贴菱形顶边与「否」支路底边，减少上下留白
    ax.set_ylim(0.48, 2.78)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    y = 2.0
    fs = FONT["label"]
    terminator(ax, (0.6, y), 0.9, 0.58, "开始", fontsize=fs)
    process(ax, (1.85, y), 1.25, 0.82, "拉取增量\nSMART 日志", fontsize=fs)
    process(ax, (3.25, y), 1.05, 0.72, "数据预处理", fontsize=fs)
    process(ax, (4.6, y), 1.15, 0.72, "特征/标签\n构造", fontsize=fs)
    process(ax, (5.95, y), 1.05, 0.72, "模型推理", fontsize=fs)
    decision(ax, (7.35, y), 1.4, 1.28, "满足预警\n条件？", fontsize=fs)
    process(ax, (8.85, y), 1.05, 0.72, "预警写入", fontsize=fs)
    terminator(ax, (10.25, y), 0.9, 0.58, "结束", fontsize=fs)

    arrow(ax, (1.05, y), (1.225, y))
    arrow(ax, (2.475, y), (2.725, y))
    arrow(ax, (3.775, y), (4.025, y))
    arrow(ax, (5.175, y), (5.425, y))
    arrow(ax, (6.475, y), (6.65, y))
    arrow(ax, (8.05, y), (8.325, y))
    edge_label(ax, (8.18, 2.22), "是")
    arrow(ax, (9.375, y), (9.8, y))

    routed_arrow(
        ax,
        [(7.35, 1.36), (7.35, 0.62), (10.25, 0.62), (10.25, 1.71)],
    )
    edge_label(ax, (7.35, 1.02), "否")

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
