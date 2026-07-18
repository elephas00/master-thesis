"""第三章：盘级 TP/FP/TN/FN 判定示意。

色调对齐架构图（chap1-framework / chap3-pipeline）Material 语义色；
形态上保留实心/虚线边差异，灰度打印仍可区分。

生成 figure/chap3-tp-tn-fp-fn.pdf。

用法（项目根目录）:
    python3 figure_codes/chap3_tp_tn_fp_fn.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from flowchart_style import INK, apply_flowchart_rc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap3-tp-tn-fp-fn.pdf"

# 与 chap3-tp-tn-fp-fn.xml / 架构图一致；FN 虚线边便于黑白区分
STYLE = {
    "TP": {"facecolor": "#4CAF50", "edgecolor": "#2E7D32", "linestyle": "solid"},
    "FP": {"facecolor": "#E53935", "edgecolor": "#B71C1C", "linestyle": "solid"},
    "TN": {"facecolor": "#1E88E5", "edgecolor": "#0D47A1", "linestyle": "solid"},
    "FN": {"facecolor": "#FFF8E1", "edgecolor": "#F57F17", "linestyle": (0, (3, 2))},
}
C_WINDOW = "#C8E6C9"
C_WINDOW_EDGE = "#2E7D32"
C_T0 = "#E53935"
C_FLOW = "#90A4AE"
C_MUTED = "#546E7A"


def _marker(ax, x: float, y: float, kind: str, r: float = 0.13) -> None:
    st = STYLE[kind]
    ax.add_patch(Circle(
        (x, y), r,
        facecolor=st["facecolor"],
        edgecolor=st["edgecolor"],
        linewidth=1.4,
        linestyle=st["linestyle"],
        zorder=3,
    ))


def _timeline(ax, x0: float, x1: float, y: float) -> None:
    ax.plot([x0, x1], [y, y], color="#757575", linewidth=2.2, solid_capstyle="butt", zorder=1)
    ax.annotate(
        "",
        xy=(x1 + 0.25, y),
        xytext=(x1, y),
        arrowprops={
            "arrowstyle": "-|>",
            "color": "#757575",
            "linewidth": 2.0,
            "mutation_scale": 12,
            "shrinkA": 0,
            "shrinkB": 0,
        },
        zorder=1,
    )


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    ax.set_xlim(0.2, 14.6)
    ax.set_ylim(0.2, 7.4)
    ax.axis("off")

    # ---- 图例 ----
    ax.text(0.5, 7.05, "图例", fontsize=11, fontweight="bold", color=INK)
    legend = [
        (2.0, "TP", "TP（窗口内预警）"),
        (5.2, "FP", "FP（误报）"),
        (7.8, "TN", "TN（正确不预警）"),
        (11.0, "FN", "FN（窗口内未预警）"),
    ]
    for x, kind, label in legend:
        _marker(ax, x, 7.05, kind, r=0.12)
        ax.text(x + 0.28, 7.05, label, ha="left", va="center", fontsize=9.5, color=INK)

    # ---- 时间流向 ----
    ax.text(0.5, 6.35, "时间流向", fontsize=10, fontweight="bold", color=C_MUTED)
    ax.text(2.0, 6.35, "更早", fontsize=9.5, color=C_MUTED, ha="left", va="center")
    ax.plot([2.7, 11.8], [6.35, 6.35], color=C_FLOW, linewidth=2.5, zorder=1)
    ax.annotate(
        "",
        xy=(12.15, 6.35),
        xytext=(11.8, 6.35),
        arrowprops={
            "arrowstyle": "-|>",
            "color": C_FLOW,
            "linewidth": 2.2,
            "mutation_scale": 11,
            "shrinkA": 0,
            "shrinkB": 0,
        },
        zorder=1,
    )
    ax.text(12.4, 6.35, "更晚", fontsize=9.5, color=C_MUTED, ha="left", va="center")

    # ---- 行 1：有故障 ----
    y1 = 4.55
    ax.text(0.5, 5.55, "1）有故障：故障发生时刻 $t_0$", fontsize=10.5, fontweight="bold", color=INK)

    win_x0, win_x1 = 7.2, 11.0
    ax.add_patch(Rectangle(
        (win_x0, y1 - 0.45),
        win_x1 - win_x0,
        0.9,
        facecolor=C_WINDOW,
        edgecolor="#B0BEC5",
        linewidth=0.8,
        alpha=0.55,
        zorder=0,
    ))
    ax.plot([win_x0, win_x0], [y1 - 0.45, y1 + 0.45], color=C_WINDOW_EDGE, linewidth=1.6, zorder=2)
    ax.text(
        (win_x0 + win_x1) / 2, y1 + 0.72,
        "时间窗口：$t_0{-}30\\mathrm{d} \\rightarrow t_0$",
        ha="center", va="center", fontsize=9, color=C_WINDOW_EDGE,
    )
    ax.text(
        win_x0 - 0.15, y1 + 0.72, "$t_0{-}30\\mathrm{d}$",
        ha="right", va="center", fontsize=9, color=C_WINDOW_EDGE,
    )

    _timeline(ax, 1.8, 11.0, y1)

    t0 = 11.0
    ax.plot([t0, t0], [y1 - 0.7, y1 + 0.7], color=C_T0, linewidth=2.0, zorder=2)
    ax.text(t0 + 0.2, y1 + 0.45, "故障发生 $t_0$", ha="left", va="center", fontsize=9.5, color=INK)

    _marker(ax, 4.0, y1, "FP")
    ax.text(4.0, y1 - 0.75, "FP：窗口前预警", ha="center", va="center", fontsize=9)

    _marker(ax, 8.5, y1, "TP")
    ax.text(8.5, y1 - 0.75, "TP：窗口内预警", ha="center", va="center", fontsize=9)

    _marker(ax, 9.9, y1, "FN")
    ax.text(9.9, y1 - 0.75, "FN：全程未预警", ha="center", va="center", fontsize=9)

    # ---- 行 2：无故障 TN ----
    y2 = 2.55
    ax.text(0.5, 3.35, "2）无故障：无误报 ⇒ TN", fontsize=10.5, fontweight="bold", color=INK)
    _timeline(ax, 1.8, 13.2, y2)
    _marker(ax, 7.5, y2, "TN", r=0.14)
    ax.text(7.5, y2 - 0.7, "TN：全程不触发预警", ha="center", va="center", fontsize=9)

    # ---- 行 3：无故障 FP ----
    y3 = 0.85
    ax.text(0.5, 1.65, "3）无故障：发生误报 ⇒ FP", fontsize=10.5, fontweight="bold", color=INK)
    _timeline(ax, 1.8, 13.2, y3)
    _marker(ax, 7.5, y3, "FP", r=0.14)
    ax.text(7.5, y3 - 0.55, "FP：无故障但触发预警", ha="center", va="center", fontsize=9)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
