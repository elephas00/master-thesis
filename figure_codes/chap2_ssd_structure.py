"""第二章：NAND 闪存分层组织结构

生成 figure/generated/chap2-ssd-structure.pdf。
展示 LUN → Plane → Block → Page 层级关系，
以及底部的页缓存与闪存缓存。

用法（项目根目录）:
    python3 figure_codes/chap2_ssd_structure.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from matplotlib.patches import FancyBboxPatch
from thesis_style import FONT

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap2-ssd-structure.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": FONT["label"],
    # 以 TrueType(Type42) 嵌入字体，保证 PDF 内文字可选中/复制/搜索
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# 配色 —— 黑白教材风格：白底黑框
C_LUN_FILL = "#FFFFFF"
C_LUN_EDGE = "#000000"
C_PLANE_FILL = "#FFFFFF"
C_PLANE_EDGE = "#000000"
C_BLK_FILL = "#FFFFFF"
C_BLK_EDGE = "#000000"
C_PG_FILL = "#FFFFFF"
C_PG_EDGE = "#000000"
C_CACHE_FILL = "#FFFFFF"
C_CACHE_EDGE = "#000000"
C_TEXT = "#000000"
C_MUTED = "#000000"


def _box(ax, xy, w, h, text, fc, ec, fs=FONT["label"], weight="bold", lw=1.4):
    """绘制方角矩形并居中放置文本。"""
    p = FancyBboxPatch(
        xy, w, h,
        boxstyle="square,pad=0.02",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2,
    )
    ax.add_patch(p)
    if text:
        ax.text(xy[0] + w / 2, xy[1] + h / 2, text,
                ha="center", va="center", fontsize=fs,
                fontweight=weight, color=C_TEXT, zorder=3)


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(11, 7.6))
    ax.set_xlim(-2, 102)
    # LUN 外框顶约 y=80，上沿贴紧内容，去掉层级说明后的多余留白
    ax.set_ylim(0, 81.5)
    ax.axis("off")

    def _draw_block(bx, by, bw, bh, name):
        """块内纵向排列 页0 / 页1 / ○○○ / 页255。"""
        _box(ax, (bx, by), bw, bh, None, C_BLK_FILL, C_BLK_EDGE, lw=1.2)
        ax.text(bx + bw / 2, by + bh - 0.8, name,
                ha="center", va="top", fontsize=FONT["title"],
                fontweight="bold", color=C_BLK_EDGE, zorder=3)
        pgw = bw - 4
        pgx = bx + 2
        pgh = 3.2
        top = by + bh - 7.0
        _box(ax, (pgx, top), pgw, pgh, "页0",
             C_PG_FILL, C_PG_EDGE, fs=FONT["tick"], weight="normal", lw=0.8)
        _box(ax, (pgx, top - 4.2), pgw, pgh, "页1",
             C_PG_FILL, C_PG_EDGE, fs=FONT["tick"], weight="normal", lw=0.8)
        ax.text(bx + bw / 2, top - 6.2, "⋯",
                ha="center", va="center", fontsize=FONT["label"], color=C_TEXT)
        _box(ax, (pgx, top - 10.4), pgw, pgh, "页255",
             C_PG_FILL, C_PG_EDGE, fs=FONT["tick"], weight="normal", lw=0.8)

    def _draw_plane(px, py, pw, ph, plane_idx):
        """一个 Plane 竖列：块 → … → 块 → 页缓存 → 闪存缓存。"""
        plane = FancyBboxPatch(
            (px, py), pw, ph, boxstyle="square,pad=0.2",
            facecolor=C_PLANE_FILL, edgecolor=C_PLANE_EDGE,
            linewidth=1.4, zorder=1,
        )
        ax.add_patch(plane)
        ax.text(px + pw / 2, py + ph - 1.5, f"Plane{plane_idx}",
                ha="center", va="top", fontsize=FONT["title"] + 1.5,
                fontweight="bold", color=C_PLANE_EDGE, zorder=3)
        bw = pw - 4
        bx = px + 2
        # 块自上而下堆叠
        _draw_block(bx, py + 44, bw, 18, "块0")
        ax.text(px + pw / 2, py + 43, "⋯",
                ha="center", va="center", fontsize=FONT["title"] + 5,
                color=C_TEXT, fontweight="bold")
        _draw_block(bx, py + 24, bw, 18, "块1023")
        # 页缓存 / 闪存缓存：位于每个 Plane 列底部
        _box(ax, (bx, py + 12), bw, 9, "页缓存",
             C_CACHE_FILL, C_CACHE_EDGE, fs=FONT["title"], lw=1.1)
        _box(ax, (bx, py + 2), bw, 9, "闪存缓存",
             C_CACHE_FILL, C_CACHE_EDGE, fs=FONT["title"], lw=1.1)

    lun_w = 45
    plane_w = 19.5
    for lname, lx in [("LUN0", 1), ("LUN7", 54)]:
        # ---- LUN 外框 ----
        lun = FancyBboxPatch(
            (lx, 2), lun_w, 78, boxstyle="square,pad=0.3",
            facecolor=C_LUN_FILL, edgecolor=C_LUN_EDGE,
            linewidth=2.2, zorder=0,
        )
        ax.add_patch(lun)
        ax.text(lx + lun_w / 2, 78.5, lname,
                ha="center", va="top", fontsize=FONT["title"] + 5,
                fontweight="bold", color=C_LUN_EDGE, zorder=3)
        # ---- 两个并排 Plane，各自含块与缓存 ----
        for pi in range(2):
            px = lx + 2 + pi * (plane_w + 2)
            _draw_plane(px, 5, plane_w, 69, pi)

    # LUN 间横向省略
    ax.text(50, 40, "⋯", ha="center", va="center",
            fontsize=int(FONT["title"] * 2.5), color=C_TEXT, fontweight="bold")

    return fig


def main() -> None:
    ensure_output_dirs()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot()
    fig.savefig(OUT_PDF, bbox_inches="tight", facecolor="white", pad_inches=0.06)
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()