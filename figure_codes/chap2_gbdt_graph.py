"""第二章：GBDT 基本训练流程（黑白印刷版）。

生成 figure/generated/chap2-gbdt.pdf。

用法（项目根目录）:
    python3 figure_codes/chap2_gbdt_graph.py
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
    terminator,
)
from thesis_style import FONT

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap2-gbdt.pdf"


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(9.6, 3.35))
    ax.set_xlim(-0.1, 13.4)
    ax.set_ylim(0.7, 6.1)
    ax.axis("off")

    y_top, y_bottom = 5.2, 1.85
    fs = FONT["label"]
    gap = 0.5  # 顶行水平箭头统一间隙
    box_h = 1.55       # 处理框统一高度
    term_h = 0.85      # 起止框
    dec_w, dec_h = 2.9, 2.05

    # ---- 顶行：起止与处理框（由左向右用固定 gap 串联）----
    start_c, start_w = 0.7, 1.1
    init_w, grad_w, cart_w = 3.5, 3.3, 3.3
    start_r = start_c + start_w / 2
    init_c = start_r + gap + init_w / 2
    init_r = init_c + init_w / 2
    grad_c = init_r + gap + grad_w / 2
    grad_r = grad_c + grad_w / 2
    cart_c = grad_r + gap + cart_w / 2

    terminator(ax, (start_c, y_top), start_w, term_h, "开始", fontsize=fs)
    process(
        ax, (init_c, y_top), init_w, box_h,
        "初始化模型\n$F_0(x)=\\arg\\min_c\\sum_i L(y_i,c)$", fontsize=fs,
    )
    process(
        ax, (grad_c, y_top), grad_w, box_h,
        "计算负梯度（伪残差）\n"
        "$r_{it}=-\\partial L/\\partial F_{t-1}$",
        fontsize=fs,
    )
    process(
        ax, (cart_c, y_top), cart_w, box_h,
        "训练第 $t$ 棵 CART 树 $f_t(x)$\n拟合伪残差 $r_{it}$",
        fontsize=fs,
    )

    update_w = 3.4
    update_c = cart_c
    process(
        ax, (update_c, y_bottom), update_w, box_h,
        "更新模型\n$F_t(x)=F_{t-1}(x)+\\eta f_t(x)$",
        fontsize=fs,
    )

    arrow(ax, (start_r, y_top), (init_c - init_w / 2, y_top))
    arrow(ax, (init_r, y_top), (grad_c - grad_w / 2, y_top))
    arrow(ax, (grad_r, y_top), (cart_c - cart_w / 2, y_top))

    arrow(ax, (cart_c, y_top - box_h / 2), (update_c, y_bottom + box_h / 2))

    # ---- 底行：判断对齐负梯度框，使「否」竖直向上 ----
    out_w = 3.7
    dec_c = grad_c
    dec_l = dec_c - dec_w / 2
    dec_r = dec_c + dec_w / 2
    update_l = update_c - update_w / 2
    gap_yes = gap * 1.25  # 「是」箭头加长约 1/4
    out_c = dec_l - gap_yes - out_w / 2

    decision(
        ax, (dec_c, y_bottom), dec_w, dec_h,
        "是否达到最大\n迭代次数 $T$？", fontsize=fs,
    )
    arrow(ax, (update_l, y_bottom), (dec_r, y_bottom))

    process(
        ax,
        (out_c, y_bottom),
        out_w,
        box_h,
        "输出最终模型\n$F_T(x)=F_0(x)+\\eta\\sum_{t=1}^{T}f_t(x)$",
        fontsize=fs,
    )
    arrow(ax, (dec_l, y_bottom), (out_c + out_w / 2, y_bottom))
    # 「是」紧贴左向箭头上方
    yes_x = (dec_l + out_c + out_w / 2) / 2
    edge_label(ax, (yes_x, y_bottom + 0.32), "是", fontsize=fs)

    # 「否」：竖直向上；标签贴在箭头右侧中段
    no_y0 = y_bottom + dec_h / 2
    no_y1 = y_top - box_h / 2
    arrow(ax, (dec_c, no_y0), (dec_c, no_y1))
    edge_label(ax, (dec_c + 0.42, (no_y0 + no_y1) / 2), "否", fontsize=fs)

    end_c, end_w = 0.7, 1.1
    terminator(ax, (end_c, y_bottom), end_w, term_h, "结束", fontsize=fs)
    arrow(ax, (out_c - out_w / 2, y_bottom), (end_c + end_w / 2, y_bottom))

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
