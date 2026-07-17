"""第二章：GBDT 基本训练流程（黑白印刷版）。

生成 figure/chap2-gbdt.pdf。

用法（项目根目录）:
    python3 figure_codes/chap2_gbdt_graph.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from flowchart_style import (
    apply_flowchart_rc,
    arrow,
    decision,
    edge_label,
    process,
    terminator,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap2-gbdt.pdf"


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(9.2, 3.1))
    ax.set_xlim(-0.1, 13.2)
    ax.set_ylim(0.9, 5.9)
    ax.axis("off")

    y_top, y_bottom = 5.1, 1.9
    terminator(ax, (0.7, y_top), 1.1, 0.7, "开始", fontsize=9.2)
    process(
        ax, (3.25, y_top), 3.1, 1.25,
        "初始化模型\n$F_0(x)=\\arg\\min_c\\sum_i L(y_i,c)$", fontsize=9.0,
    )
    process(
        ax, (6.9, y_top), 3.3, 1.25,
        "计算负梯度（伪残差）\n"
        "$r_{it}=-\\partial L/\\partial F_{t-1}$",
        fontsize=8.8,
    )
    process(
        ax, (11.2, y_top), 3.3, 1.25,
        "训练第 $t$ 棵 CART 树 $f_t(x)$\n拟合伪残差 $r_{it}$",
        fontsize=9.0,
    )
    process(
        ax, (11.2, y_bottom), 3.4, 1.25,
        "更新模型\n$F_t(x)=F_{t-1}(x)+\\eta f_t(x)$",
        fontsize=9.0,
    )

    arrow(ax, (1.25, y_top), (1.7, y_top))
    arrow(ax, (4.8, y_top), (5.25, y_top))
    arrow(ax, (8.55, y_top), (9.55, y_top))
    arrow(ax, (11.2, 4.475), (11.2, 2.525))

    decision(
        ax, (6.9, y_bottom), 2.8, 1.7,
        "是否达到最大\n迭代次数 $T$？", fontsize=9.0,
    )
    arrow(ax, (9.5, y_bottom), (8.3, y_bottom))

    process(
        ax,
        (3.25, y_bottom),
        3.7,
        1.35,
        "输出最终模型\n$F_T(x)=F_0(x)+\\eta\\sum_{t=1}^{T}f_t(x)$",
        fontsize=8.8,
    )
    arrow(ax, (5.5, y_bottom), (5.1, y_bottom))
    edge_label(ax, (5.3, 2.18), "是")

    arrow(ax, (6.9, 2.75), (6.9, 4.475))
    edge_label(ax, (7.18, 3.55), "否")

    terminator(ax, (0.7, y_bottom), 1.1, 0.7, "结束", fontsize=9.2)
    arrow(ax, (1.4, y_bottom), (1.25, y_bottom))

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
