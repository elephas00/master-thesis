"""第三章：盘级 TP/FP/TN/FN 判定示意。

色调对齐架构图 Material 语义色；形态按「是否预警」二分：
  有预警 → 实心圆（TP 干净 / FP 加 X）
  无预警 → 空心圆（TN 实线空心 / FN 虚边+中心点）
灰阶打印靠填充与符号区分，避免圆内「/」被误读为禁止。

生成 figure/generated/chap3-tp-tn-fp-fn.pdf。

用法（项目根目录）:
    python3 figure_codes/chap3_tp_tn_fp_fn.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from flowchart_style import INK, apply_flowchart_rc
from thesis_style import FONT, TEXT_WIDTH_IN, savefig_text_width

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap3-tp-tn-fp-fn.pdf"

# 语义色；TN 浅底空心以与实心 TP/FP 对照
STYLE = {
    "TP": {"facecolor": "#4CAF50", "edgecolor": "#2E7D32", "linestyle": "solid", "lw": 1.4},
    "FP": {"facecolor": "#E53935", "edgecolor": "#B71C1C", "linestyle": "solid", "lw": 1.4},
    "TN": {"facecolor": "#E3F2FD", "edgecolor": "#0D47A1", "linestyle": "solid", "lw": 1.8},
    "FN": {"facecolor": "#FFF8E1", "edgecolor": "#F57F17", "linestyle": (0, (3, 2)), "lw": 1.5},
}
C_MARK = "#FAFAFA"
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
        linewidth=st["lw"],
        linestyle=st["linestyle"],
        zorder=3,
    ))
    if kind == "FP":
        d = r * 0.48
        kw = {"color": C_MARK, "linewidth": 1.35, "solid_capstyle": "round", "zorder": 4}
        ax.plot([x - d, x + d], [y - d, y + d], **kw)
        ax.plot([x - d, x + d], [y + d, y - d], **kw)
    elif kind == "FN":
        ax.add_patch(Circle(
            (x, y), r * 0.28,
            facecolor=st["edgecolor"],
            edgecolor=st["edgecolor"],
            linewidth=0.6,
            zorder=4,
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
    # 栏宽出图；字号降一档；整体压矮
    fs_h = FONT["tick"]       # 原 label 10 → 9
    fs_b = FONT["note"] - 1   # 原 note 8 → 7
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 2.95))
    ax.set_xlim(0.2, 14.7)
    ax.set_ylim(0.0, 6.35)
    ax.axis("off")

    # 左：「图例」；右上行四项自左排布，余量均分到项间距
    x_lab, x_left, x_right = 0.35, 1.85, 13.85
    y_leg, y_time = 6.05, 5.5
    ax.text(
        x_lab, 0.5 * (y_leg + y_time), "图例",
        fontsize=fs_h, fontweight="bold", color=INK, va="center",
    )

    legend_items = [
        ("TP", "TP（窗口内预警）", 2.55),
        ("FP", "FP（误报）", 1.55),
        ("TN", "TN（正确不预警）", 2.55),
        ("FN", "FN（窗口内未预警）", 2.65),
    ]
    mark_to_text = 0.42
    item_w = [mark_to_text + tw for _, _, tw in legend_items]
    n = len(legend_items)
    spare = (x_right - x_left) - sum(item_w)
    gap = max(spare / (n - 1), 0.35) if n > 1 else 0.0
    x = x_left
    for (kind, label, _), w in zip(legend_items, item_w):
        _marker(ax, x + 0.12, y_leg, kind, r=0.11)
        ax.text(x + mark_to_text, y_leg, label, ha="left", va="center",
                fontsize=fs_b, color=INK)
        x += w + gap

    ax.text(x_left, y_time, "时间流向：更早", fontsize=fs_b, color=C_MUTED,
            ha="left", va="center")
    ax.plot([x_left + 2.35, x_right - 0.85], [y_time, y_time], color=C_FLOW, linewidth=2.2, zorder=1)
    ax.annotate(
        "",
        xy=(x_right - 0.5, y_time),
        xytext=(x_right - 0.85, y_time),
        arrowprops={
            "arrowstyle": "-|>",
            "color": C_FLOW,
            "linewidth": 2.0,
            "mutation_scale": 10,
            "shrinkA": 0,
            "shrinkB": 0,
        },
        zorder=1,
    )
    ax.text(x_right - 0.35, y_time, "更晚", fontsize=fs_b, color=C_MUTED,
            ha="left", va="center")

    # ---- 行 1：有故障 ----
    y1 = 3.85
    half = 0.34
    ax.text(0.4, 4.85, "1）有故障：故障发生时刻 $t_0$", fontsize=fs_h, fontweight="bold", color=INK)

    win_x0, win_x1 = 6.4, 12.35
    ax.add_patch(Rectangle(
        (win_x0, y1 - half),
        win_x1 - win_x0,
        2 * half,
        facecolor=C_WINDOW,
        edgecolor="#B0BEC5",
        linewidth=0.8,
        alpha=0.55,
        zorder=0,
    ))
    ax.plot([win_x0, win_x0], [y1 - half, y1 + half], color=C_WINDOW_EDGE, linewidth=1.5, zorder=2)
    y_cap = y1 + 0.48
    ax.text(
        (win_x0 + win_x1) / 2, y_cap,
        "时间窗口：$t_0{-}30\\mathrm{d}\\rightarrow t_0$",
        ha="center", va="center", fontsize=fs_b, color=C_WINDOW_EDGE,
    )
    ax.text(
        win_x0, y_cap, "$t_0{-}30\\mathrm{d}$",
        ha="center", va="center", fontsize=fs_b, color=C_WINDOW_EDGE,
    )

    _timeline(ax, 1.9, 12.35, y1)

    t0 = 12.35
    ax.plot([t0, t0], [y1 - half, y1 + half], color=C_T0, linewidth=1.8, zorder=2)
    ax.text(t0, y_cap, "故障发生 $t_0$", ha="center", va="center",
            fontsize=fs_b, color=INK)

    y_lab = y1 - 0.52
    _marker(ax, 3.7, y1, "FP", r=0.11)
    ax.text(3.7, y_lab, "FP：窗口前预警", ha="center", va="center", fontsize=fs_b)

    _marker(ax, 7.2, y1, "TP", r=0.11)
    ax.text(7.2, y_lab, "TP：窗口内预警", ha="center", va="center", fontsize=fs_b)

    _marker(ax, 10.35, y1, "FN", r=0.11)
    ax.text(10.35, y_lab, "FN：全程未预警", ha="center", va="center", fontsize=fs_b)

    # ---- 行 2：无故障 TN ----
    y2 = 1.9
    ax.text(0.4, 2.5, "2）无故障：无误报 ⇒ TN", fontsize=fs_h, fontweight="bold", color=INK)
    t2_x0, t2_x1 = 1.7, 13.1
    _timeline(ax, t2_x0, t2_x1, y2)
    x_tn = t2_x0 + (t2_x1 - t2_x0) * (2 / 3)
    _marker(ax, x_tn, y2, "TN", r=0.12)
    ax.text(x_tn, y2 - 0.48, "TN：全程不触发预警", ha="center", va="center", fontsize=fs_b)

    # ---- 行 3：无故障 FP ----
    y3 = 0.48
    ax.text(0.4, 1.08, "3）无故障：发生误报 ⇒ FP", fontsize=fs_h, fontweight="bold", color=INK)
    t3_x0, t3_x1 = 1.7, 13.1
    _timeline(ax, t3_x0, t3_x1, y3)
    x_fp = t3_x0 + (t3_x1 - t3_x0) * (2 / 3)
    _marker(ax, x_fp, y3, "FP", r=0.12)
    ax.text(x_fp, y3 - 0.42, "FP：无故障但触发预警", ha="center", va="center", fontsize=fs_b)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_pdf, pad_inches=0.02)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
