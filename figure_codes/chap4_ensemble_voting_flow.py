"""第四章：LP/MP/UP 分层建模 + 投票融合

生成 figure/chap4-ensemble-voting-flow.pdf。
配色对齐第三章异构集成示意（蓝基学习器 / 绿输出）。

用法（项目根目录）:
    python3 figure_codes/chap4_ensemble_voting_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap4-ensemble-voting-flow.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": 11,
})

C_BLUE_F, C_BLUE_E = "#E3F2FD", "#1565C0"
C_GRAY_F, C_GRAY_E = "#F5F5F5", "#757575"
C_GREEN_F, C_GREEN_E = "#E8F5E9", "#2E7D32"
C_ORANGE_F, C_ORANGE_E = "#FFF3E0", "#E65100"
C_ARROW = "#424242"
C_MUTED = "#546E7A"


def _box(ax, xy, w, h, text, fc, ec, fontsize=11):
    patch = FancyBboxPatch(
        xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.6",
        facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=2,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color="#212121", zorder=3,
            linespacing=1.25)


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.axis("off")

    # 外框（淡蓝虚线，对齐 chap3 method-bg）
    frame = FancyBboxPatch(
        (4, 4), 92, 60,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor="#F8FBFF", edgecolor="#90CAF9", linewidth=1.5,
        linestyle=(0, (6, 4)), zorder=0,
    )
    ax.add_patch(frame)

    ax.text(50, 60, "分层建模 + 多数投票", ha="center", va="center",
            fontsize=13, fontweight="bold", color=C_BLUE_E)

    # 输入
    _box(ax, (8, 38), 18, 14, "早期 PE 档位\nFBC 特征\n$\\mathbf{x}_i$", C_GRAY_F, C_GRAY_E, fontsize=10)

    # 三个页类型模型
    models = [
        (38, 48, "LightGBM\nUP"),
        (38, 30, "LightGBM\nMP"),
        (38, 12, "LightGBM\nLP"),
    ]
    for x, y, t in models:
        _box(ax, (x, y), 20, 12, t, C_BLUE_F, C_BLUE_E, fontsize=10)

    # 投票
    _box(ax, (68, 28), 22, 16, "多数投票\n（3 页类型）", C_ORANGE_F, C_ORANGE_E, fontsize=10)

    # 输出
    _box(ax, (68, 8), 22, 12, "块级标签\n强块 / 弱块", C_GREEN_F, C_GREEN_E, fontsize=10)

    # 箭头：输入 → 三模型
    for y in (54, 36, 18):
        ax.annotate(
            "", xy=(38, y), xytext=(26, 45),
            arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=1.4,
                            connectionstyle="arc3,rad=0", mutation_scale=11),
            zorder=1,
        )

    # 三模型 → 投票
    for y in (54, 36, 18):
        ax.annotate(
            "", xy=(68, 36), xytext=(58, y),
            arrowprops=dict(arrowstyle="-|>", color=C_BLUE_E, lw=1.5,
                            connectionstyle="arc3,rad=0", mutation_scale=11),
            zorder=1,
        )

    # 投票 → 输出
    ax.annotate(
        "", xy=(79, 20), xytext=(79, 28),
        arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=1.6, mutation_scale=12),
        zorder=1,
    )

    ax.text(17, 32, "分别建模\n（防过拟合）", ha="center", va="center",
            fontsize=8.5, color=C_MUTED)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", facecolor="white")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
