"""第五章：预警处置交互流程（黑白印刷版）。

生成 figure/generated/chap5-warning-handle-flow.pdf。

用法（项目根目录）:
    python3 figure_codes/chap5_warning_handle_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from flowchart_style import (
    INK,
    LINE_WIDTH,
    PAPER,
    apply_flowchart_rc,
    arrow,
    dashed_arrow,
    process,
    routed_arrow,
    routed_dashed_arrow,
)
from thesis_style import FONT

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap5-warning-handle-flow.pdf"

LANES = ("运维人员", "前端页面", "后端服务", "数据库")
LX = (1.4, 3.95, 6.5, 9.0)
LW = (2.3, 2.5, 2.5, 2.3)


def _lane(ax, x: float, w: float, title: str, *, y0: float, h: float, head_h: float) -> None:
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y0), w, h,
        boxstyle="square,pad=0",
        facecolor=PAPER, edgecolor=INK, linewidth=LINE_WIDTH, zorder=0,
    ))
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y0 + h - head_h), w, head_h,
        boxstyle="square,pad=0",
        facecolor="#F2F2F2", edgecolor=INK, linewidth=LINE_WIDTH, zorder=1,
    ))
    ax.text(
        x, y0 + h - head_h / 2, title, ha="center", va="center",
        fontsize=FONT["label"], color=INK, fontweight="bold", zorder=2,
    )


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(10.0, 3.2))
    ax.set_xlim(0.05, 10.3)
    ax.set_ylim(0.06, 3.72)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    lane_y0, lane_h, head_h = 0.10, 3.52, 0.36
    for x, w, title in zip(LX, LW, LANES):
        _lane(ax, x, w, title, y0=lane_y0, h=lane_h, head_h=head_h)

    bh, bh2, bh3 = 0.52, 0.55, 0.70
    fs, fs2 = FONT["annot"], FONT["note"]
    hw1, hw2, hw4 = 0.95, 1.0, 0.95

    # 表头底约 3.26；① 顶边留约 0.12 间距
    u1 = (LX[0], 2.88)
    f2 = (LX[1], 2.32)
    b2 = (LX[2], 2.32)
    u3 = (LX[0], 1.74)
    f4 = (LX[1], 1.16)
    b4 = (LX[2], 1.16)
    d5 = (LX[3], 1.16)
    b6 = (LX[2], 0.44)
    f6 = (LX[1], 0.44)

    process(ax, u1, 1.9, bh, "① 查看预警\n列表与详情", fontsize=fs)
    process(ax, f2, 2.0, bh, "② 请求预警\n详情接口", fontsize=fs)
    process(ax, b2, 2.0, bh, "返回评分、状态", fontsize=fs)
    process(ax, u3, 1.9, bh2, "③ 选择确认故障\n或忽略预警", fontsize=fs)
    process(ax, f4, 2.0, bh, "④ 提交状态\n更新请求", fontsize=fs)
    process(ax, b4, 2.0, bh, "⑤ 校验预警状态", fontsize=fs)
    process(ax, d5, 1.9, bh3, "更新预警状态\n与处置时间\n（确认时写故障）", fontsize=fs2)
    process(ax, b6, 2.0, bh, "返回处置结果", fontsize=fs)
    process(ax, f6, 2.0, bh, "⑥ 刷新列表\n与详情展示", fontsize=fs)

    # L 形两折：先水平到目标中线，再竖直进入顶边
    routed_arrow(ax, [
        (u1[0] + hw1, u1[1]),
        (f2[0], u1[1]),
        (f2[0], f2[1] + bh / 2),
    ])
    arrow(ax, (f2[0] + hw2, f2[1] + 0.08), (b2[0] - hw2, b2[1] + 0.08))
    dashed_arrow(ax, (b2[0] - hw2, b2[1] - 0.1), (f2[0] + hw2, f2[1] - 0.1))
    routed_dashed_arrow(ax, [
        (f2[0] - hw2, f2[1]),
        (u3[0], f2[1]),
        (u3[0], u3[1] + bh2 / 2),
    ])
    routed_arrow(ax, [
        (u3[0] + hw1, u3[1]),
        (f4[0], u3[1]),
        (f4[0], f4[1] + bh / 2),
    ])
    arrow(ax, (f4[0] + hw2, f4[1]), (b4[0] - hw2, b4[1]))
    arrow(ax, (b4[0] + hw2, b4[1]), (d5[0] - hw4, b4[1]))
    routed_dashed_arrow(ax, [
        (d5[0], d5[1] - bh3 / 2),
        (d5[0], b6[1]),
        (b6[0] + hw2, b6[1]),
    ])
    dashed_arrow(ax, (b6[0] - hw2, b6[1]), (f6[0] + hw2, f6[1]))

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
