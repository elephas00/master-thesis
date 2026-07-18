"""第五章：预警处置交互流程（黑白印刷版）。

生成 figure/chap5-warning-handle-flow.pdf。

用法（项目根目录）:
    python3 figure_codes/chap5_warning_handle_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap5-warning-handle-flow.pdf"

LANES = ("运维人员", "前端页面", "后端服务", "数据库")
LX = (1.4, 3.95, 6.5, 9.0)
LW = (2.3, 2.5, 2.5, 2.3)


def _lane(ax, x: float, w: float, title: str) -> None:
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, 0.3), w, 5.55,
        boxstyle="square,pad=0",
        facecolor=PAPER, edgecolor=INK, linewidth=LINE_WIDTH, zorder=0,
    ))
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, 5.25), w, 0.6,
        boxstyle="square,pad=0",
        facecolor="#F2F2F2", edgecolor=INK, linewidth=LINE_WIDTH, zorder=1,
    ))
    ax.text(
        x, 5.55, title, ha="center", va="center",
        fontsize=10.5, color=INK, fontweight="bold", zorder=2,
    )


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(10.0, 5.1))
    ax.set_xlim(0.05, 10.3)
    ax.set_ylim(0.1, 6.0)
    ax.axis("off")

    for x, w, title in zip(LX, LW, LANES):
        _lane(ax, x, w, title)

    u1 = (LX[0], 4.75)
    f2 = (LX[1], 4.0)
    b2 = (LX[2], 4.0)
    u3 = (LX[0], 3.0)
    f4 = (LX[1], 2.05)
    b4 = (LX[2], 2.05)
    d5 = (LX[3], 1.9)
    b6 = (LX[2], 0.75)
    f6 = (LX[1], 0.75)

    process(ax, u1, 1.9, 0.75, "① 查看预警\n列表与详情", fontsize=8.8)
    process(ax, f2, 2.0, 0.7, "② 请求预警\n详情接口", fontsize=8.8)
    process(ax, b2, 2.0, 0.7, "返回评分、状态", fontsize=8.8)
    process(ax, u3, 1.9, 0.8, "③ 选择确认故障\n或忽略预警", fontsize=8.8)
    process(ax, f4, 2.0, 0.7, "④ 提交状态\n更新请求", fontsize=8.8)
    process(ax, b4, 2.0, 0.7, "⑤ 校验预警状态", fontsize=8.8)
    process(ax, d5, 1.9, 0.95, "更新预警状态\n与处置时间\n（确认时写故障）", fontsize=8.2)
    process(ax, b6, 2.0, 0.7, "返回处置结果", fontsize=8.8)
    process(ax, f6, 2.0, 0.7, "⑥ 刷新列表\n与详情展示", fontsize=8.8)

    # ① → ②
    routed_arrow(ax, [
        (u1[0] + 0.95, u1[1] - 0.375),
        (u1[0] + 0.95, 4.45),
        (f2[0] - 1.0, 4.45),
        (f2[0] - 1.0, f2[1] + 0.35),
    ])
    # ② → 后端
    arrow(ax, (f2[0] + 1.0, f2[1] + 0.1), (b2[0] - 1.0, b2[1] + 0.1))
    # 后端 ⇢ ②（返回）
    dashed_arrow(ax, (b2[0] - 1.0, b2[1] - 0.15), (f2[0] + 1.0, f2[1] - 0.15))
    # ② ⇢ ③
    routed_dashed_arrow(ax, [
        (f2[0] - 0.55, f2[1] - 0.35),
        (f2[0] - 0.55, 3.55),
        (u3[0] + 0.95, 3.55),
        (u3[0] + 0.95, u3[1] + 0.4),
    ])
    # ③ → ④
    routed_arrow(ax, [
        (u3[0] + 0.95, u3[1] - 0.4),
        (u3[0] + 0.95, 2.55),
        (f4[0] - 1.0, 2.55),
        (f4[0] - 1.0, f4[1] + 0.35),
    ])
    # ④ → ⑤
    arrow(ax, (f4[0] + 1.0, f4[1]), (b4[0] - 1.0, b4[1]))
    # ⑤ → DB
    arrow(ax, (b4[0] + 1.0, b4[1] - 0.05), (d5[0] - 0.95, d5[1] + 0.2))
    # DB ⇢ 返回处置结果
    routed_dashed_arrow(ax, [
        (d5[0], d5[1] - 0.475),
        (d5[0], 1.25),
        (b6[0] + 1.0, 1.25),
        (b6[0] + 1.0, b6[1] + 0.35),
    ])
    # 返回 ⇢ ⑥
    dashed_arrow(ax, (b6[0] - 1.0, b6[1]), (f6[0] + 1.0, f6[1]))

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
