"""第二章：闪存擦写原理（浮栅晶体管）

1:1 复刻 figure/SSD读写原理.png，生成更清晰的矢量图：
    figure/generated/chap2-program-erase-principle.pdf

用法（项目根目录）:
    python3 figure_codes/chap2_program_erase_principle.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
import matplotlib.path as mpath
from matplotlib.patches import Circle, PathPatch, Polygon, Rectangle
import numpy as np
from thesis_style import FONT

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap2-program-erase-principle.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "Heiti SC", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": FONT["label"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

C_CTRL = "#7A7A7A"
C_OXIDE = "#D0D0D0"
C_FG = "#7A7A7A"        # 与控制极同色
C_SUB = "#FFFFFF"
C_EDGE = "#000000"
C_ARROW = "#111111"
C_TEXT = "#000000"
LW = 1.35


def _ground_ieee(ax, x, y, scale=1.0, lw=LW):
    """电路接地符号（Earth/GND）：三根递减横线。"""
    widths = [15 * scale, 9.5 * scale, 4 * scale]
    gap = 3.4 * scale
    for i, w in enumerate(widths):
        yy = y - i * gap
        ax.plot([x - w / 2, x + w / 2], [yy, yy], color=C_EDGE, lw=lw, zorder=6)


def _terminal_dot(ax, x, y, r=3.2, lw=LW):
    """连接点：空心圆 + 实心圆心（原图 a 底部在衬底下沿线处）。"""
    ax.add_patch(Circle(
        (x, y), r, facecolor="#FFFFFF", edgecolor=C_EDGE, linewidth=lw, zorder=6,
    ))
    ax.add_patch(Circle(
        (x, y), r * 0.35, facecolor=C_EDGE, edgecolor=C_EDGE, linewidth=0, zorder=7,
    ))


def _v_arrow(ax, x, y0, y1, *, tip_len=4.2, tip_w=2.6, z=6):
    """竖直箭头：全部用 Patch 绘制，便于用 zorder 压在灰底之上、文字之下。"""
    up = y1 > y0
    shaft_w = 1.15
    if up:
        base = y1 - tip_len
        ax.add_patch(Rectangle(
            (x - shaft_w / 2, y0), shaft_w, max(base - y0, 0.01),
            facecolor=C_ARROW, edgecolor="none", zorder=z, linewidth=0,
        ))
        ax.add_patch(Polygon(
            [(x, y1), (x - tip_w, base), (x + tip_w, base)],
            closed=True, facecolor=C_ARROW, edgecolor=C_ARROW, lw=0, zorder=z,
        ))
    else:
        base = y1 + tip_len
        ax.add_patch(Rectangle(
            (x - shaft_w / 2, base), shaft_w, max(y0 - base, 0.01),
            facecolor=C_ARROW, edgecolor="none", zorder=z, linewidth=0,
        ))
        ax.add_patch(Polygon(
            [(x, y1), (x - tip_w, base), (x + tip_w, base)],
            closed=True, facecolor=C_ARROW, edgecolor=C_ARROW, lw=0, zorder=z,
        ))


def _electron(ax, cx, cy, r=5.0):
    ax.add_patch(Circle(
        (cx, cy), r, facecolor="#FFFFFF", edgecolor=C_EDGE, linewidth=1.1, zorder=8,
    ))
    ax.plot([cx - r * 0.52, cx + r * 0.52], [cy, cy],
            color=C_EDGE, lw=1.3, zorder=8.5, solid_capstyle="round")


def _side_wall(ax, x, y, w, h, *, side: str):
    """竖直侧壁：圆角矩形的一半。

    内侧贴栅堆为直角，外侧顶角圆角；底边平放在衬底顶面。
    """
    r = min(w * 0.95, h * 0.25)
    Path = mpath.Path
    if side == "left":
        verts = [(x + w, y), (x + w, y + h), (x + r, y + h)]
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO]
        th = np.linspace(np.pi / 2, np.pi, 24)
        verts += list(zip(x + r + r * np.cos(th), y + h - r + r * np.sin(th)))
        codes += [Path.LINETO] * 24
        verts += [(x, y), (x + w, y)]
        codes += [Path.LINETO, Path.CLOSEPOLY]
    else:
        verts = [(x, y), (x, y + h), (x + w - r, y + h)]
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO]
        th = np.linspace(np.pi / 2, 0, 24)
        verts += list(zip(x + w - r + r * np.cos(th), y + h - r + r * np.sin(th)))
        codes += [Path.LINETO] * 24
        verts += [(x + w, y), (x, y)]
        codes += [Path.LINETO, Path.CLOSEPOLY]

    ax.add_patch(PathPatch(
        Path(verts, codes),
        facecolor=C_OXIDE, edgecolor=C_EDGE, linewidth=LW, zorder=3,
    ))


def _sd_open_arc(ax, join_x, top_y, edge_x, bot_y, *, side: str, label: str):
    """源/漏开放弧：接点 → 外侧结束于衬底左右端同一竖直投影。

    外端 x 与上下横线端点对齐；外端 y 取两条横线之间的 1/2 高度，
    不接到衬底下边线。
    """
    y_end = 0.5 * (top_y + bot_y)  # 上下横线中间
    span = abs(join_x - edge_x)
    depth = top_y - y_end
    if side == "left":
        p0 = np.array([join_x, top_y])
        p3 = np.array([edge_x, y_end])
        p1 = np.array([join_x - 0.22 * span, top_y - 0.75 * depth])
        p2 = np.array([edge_x + 0.20 * span, y_end + 0.20 * depth])
        lx = edge_x + 0.28 * span
    else:
        p0 = np.array([join_x, top_y])
        p3 = np.array([edge_x, y_end])
        p1 = np.array([join_x + 0.22 * span, top_y - 0.75 * depth])
        p2 = np.array([edge_x - 0.20 * span, y_end + 0.20 * depth])
        lx = edge_x - 0.28 * span

    t = np.linspace(0, 1, 56)[:, None]
    pts = ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
           + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)
    ax.plot(pts[:, 0], pts[:, 1], color=C_EDGE, lw=LW, zorder=2.5,
            solid_capstyle="butt", solid_joinstyle="round")
    # 文字顶对齐于衬底上边线略下方，落在顶线与开放弧之间的空隙内
    ax.text(lx, top_y - 4.0, label,
            ha="center", va="top", fontsize=FONT["label"], color=C_TEXT, zorder=8)


def _draw_cell(ax, ox: float, *, mode: str) -> None:
    # 衬底较矮，且仅上下横线（无左右边框），对齐原图
    sub_x, sub_y = ox + 18, 46
    sub_w, sub_h = 228, 30  # 衬底再压矮
    top = sub_y + sub_h

    ax.add_patch(Rectangle(
        (sub_x, sub_y), sub_w, sub_h,
        facecolor=C_SUB, edgecolor="none", linewidth=0, zorder=1,
    ))
    # 衬底上下横线均向两边延伸（两端开放，无竖边）
    ax.plot([sub_x, sub_x + sub_w], [top, top],
            color=C_EDGE, lw=LW, zorder=2, solid_capstyle="butt")
    ax.plot([sub_x, sub_x + sub_w], [sub_y, sub_y],
            color=C_EDGE, lw=LW, zorder=2, solid_capstyle="butt")

    # 栅堆几何（整体再压矮）
    wall_w = 16
    stack_w = 110
    tox_h, fg_h, ox_h, cg_h = 15, 24, 14, 17
    stack_h = tox_h + fg_h + ox_h + cg_h
    stack_x = sub_x + (sub_w - stack_w) / 2
    wall_l_x = stack_x - wall_w
    wall_r_x = stack_x + stack_w
    tox_y = top
    fg_y = tox_y + tox_h
    ox_y = fg_y + fg_h
    cg_y = ox_y + ox_h
    stack_top = cg_y + cg_h

    # 电子横坐标（先算，供源漏接点定位）
    n_e = 5
    e_r = 4.0
    e_margin = 22
    e_xs = [stack_x + e_margin + i * (stack_w - 2 * e_margin) / (n_e - 1)
            for i in range(n_e)]

    # ---- 源 / 漏接点：隧道氧化层方格下方
    # 源极：tox左边界右侧、第一个电子左侧
    # 漏极：最后一个电子右侧、tox右边界左侧
    # 外端与衬底上下横线端点同一竖直投影（sub_x / sub_x+sub_w）
    src_join = 0.5 * (stack_x + (e_xs[0] - e_r))
    drn_join = 0.5 * ((e_xs[-1] + e_r) + (stack_x + stack_w))
    _sd_open_arc(ax, src_join, top, sub_x, sub_y, side="left", label="源极")
    _sd_open_arc(ax, drn_join, top, sub_x + sub_w, sub_y, side="right", label="漏极")
    sd_ry = 0.62 * (top - sub_y)  # 供箭头下端估算

    # ---- 左右侧壁（竖直圆角矩形的一半）----
    _side_wall(ax, wall_l_x, top, wall_w, stack_h, side="left")
    _side_wall(ax, wall_r_x, top, wall_w, stack_h, side="right")

    # ---- 四层堆栈（层内文字统一用 label，避免 annot/tick/title 混用显得忽大忽小）----
    layers = [
        (tox_y, tox_h, C_OXIDE, "隧道氧化层", FONT["label"], "normal"),
        (fg_y, fg_h, C_FG, "", 0, "normal"),
        (ox_y, ox_h, C_OXIDE, "氧化层", FONT["label"], "normal"),
        (cg_y, cg_h, C_CTRL, "控制极", FONT["label"], "bold"),
    ]
    for y, h, fc, text, fs, weight in layers:
        ax.add_patch(Rectangle(
            (stack_x, y), stack_w, h,
            facecolor=fc, edgecolor=C_EDGE, linewidth=LW, zorder=4,
        ))
        if text and text != "隧道氧化层":
            ax.text(stack_x + stack_w / 2, y + h / 2, text,
                    ha="center", va="center", fontsize=fs,
                    fontweight=weight, color=C_TEXT, zorder=5)

    # 电子纵坐标
    e_y = fg_y + fg_h / 2

    # 隧穿箭头：完整贯通（浮于灰色隧道氧化层之上）
    a_bot = top - sd_ry * 0.35
    for ex in e_xs:
        if mode == "program":
            # 箭头尖停在电子下方，避免与电子重叠
            a_top = e_y - e_r - 2.8
            _v_arrow(ax, ex, a_bot, a_top, tip_len=2.6, tip_w=1.9)
        else:
            a_top = e_y - e_r + 1.5
            _v_arrow(ax, ex, a_top, a_bot, tip_len=2.6, tip_w=1.9)

    # 「隧道氧化层」白底文字浮于箭头之上（仅盖住字幅，箭头仍从上下露出）
    ax.text(
        stack_x + stack_w / 2, tox_y + tox_h / 2, "隧道氧化层",
        ha="center", va="center", fontsize=FONT["label"], color=C_TEXT, zorder=12,
        bbox=dict(
            boxstyle="square,pad=0.15",
            facecolor="#FFFFFF",
            edgecolor="none",
            alpha=1.0,
        ),
    )

    # 电子叠在箭头端点之上
    for ex in e_xs:
        _electron(ax, ex, e_y, r=e_r)

    mid_x = stack_x + stack_w / 2
    sub_bot = sub_y
    sub_mid = sub_x + sub_w / 2

    if mode == "program":
        # 控制极 → V_PP：仅竖线，无箭头
        ax.plot([mid_x, mid_x], [stack_top, stack_top + 14],
                color=C_EDGE, lw=LW, zorder=8, solid_capstyle="butt")
        ax.text(mid_x, stack_top + 16, r"$V_{PP}$",
                ha="center", va="bottom", fontsize=FONT["label"], color=C_TEXT, zorder=8)
        # 衬底底部：圆点端子 + 接地符号（三横线）
        _terminal_dot(ax, sub_mid, sub_bot, r=2.4)
        ax.plot([sub_mid, sub_mid], [sub_bot, sub_bot - 8],
                color=C_EDGE, lw=LW, zorder=8, solid_capstyle="butt")
        _ground_ieee(ax, sub_mid, sub_bot - 8, scale=0.85)
    else:
        # 控制极 → 接地（三横线 GND）
        ax.plot([mid_x, mid_x], [stack_top, stack_top + 8],
                color=C_EDGE, lw=LW, zorder=8, solid_capstyle="butt")
        _ground_ieee(ax, mid_x, stack_top + 8, scale=0.9)
        # 衬底 → V_PP：仅竖线，无箭头
        ax.plot([sub_mid, sub_mid], [sub_bot, sub_bot - 14],
                color=C_EDGE, lw=LW, zorder=8, solid_capstyle="butt")
        ax.text(sub_mid + 9, sub_bot - 11, r"$V_{PP}$",
                ha="left", va="center", fontsize=FONT["label"], color=C_TEXT, zorder=8)

    ax.text(sub_mid, sub_y + sub_h * 0.38, "衬底",
            ha="center", va="center", fontsize=FONT["label"], color=C_TEXT, zorder=5)


def plot() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(11.0, 2.7))
    ax.set_xlim(0, 540)
    # 内容约 y∈[26, 162+$V_{PP}$]：上沿贴紧 $V_{PP}$，仅留极少空白
    ax.set_ylim(24, 168)
    ax.set_aspect("equal")
    ax.axis("off")

    # 小标题上移，贴近接地下方
    _draw_cell(ax, ox=5, mode="program")
    ax.text(140, 26, "a) 写原理", fontsize=FONT["title"], fontweight="bold",
            ha="center", va="top", color=C_TEXT)

    _draw_cell(ax, ox=275, mode="erase")
    ax.text(410, 26, "b) 擦除原理", fontsize=FONT["title"], fontweight="bold",
            ha="center", va="top", color=C_TEXT)

    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    return fig


def main() -> None:
    ensure_output_dirs()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot()
    fig.savefig(OUT_PDF, bbox_inches="tight", facecolor="white", pad_inches=0.04)
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
