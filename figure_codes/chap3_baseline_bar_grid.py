"""第三章：盘级基线对比 2×4 分组柱图（方案 4）

对应 notebook `codes/eda/notebooks/eda_baseline_bar_chart.ipynb` §4。
生成 figure/generated/chap3-baseline-bar-grid.pdf。

用法（项目根目录）:
    python figure_codes/chap3_baseline_bar_grid.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    METHOD_COLORS, METHOD_HATCH, C_EDGE, C_ZERO, BAR_LW, FONT,
    TEXT_WIDTH_IN, apply_rc, fig_shared_legend, savefig_text_width,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

apply_rc()
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 300,
})

METHODS = ["本文方法", "Mut-Rule", "RF", "AE", "TCAN", "MVT-RF", "Mut-RF"]
MODELS = ["MB1", "MB2"]

# 三轮平均（与 content.tex 主结果表一致）
ROWS = [
    # model, method, TPR, FPR, Precision, F0.5
    ("MB1", "本文方法", 0.738, 2.71e-5, 0.981, 0.921),
    ("MB1", "Mut-Rule", 0.777, 1.07e-3, 0.564, 0.595),
    ("MB1", "RF",      0.765, 1.18e-4, 0.935, 0.895),
    ("MB1", "AE",      0.038, 1.34e-3, 0.043, 0.042),
    ("MB1", "TCAN",    0.000, 0.0,     0.000, 0.000),
    ("MB1", "MVT-RF",  0.769, 4.53e-5, 0.967, 0.919),
    ("MB1", "Mut-RF",  0.020, 3.63e-5, 0.500, 0.086),
    ("MB2", "本文方法", 0.187, 0.0,     1.000, 0.490),
    ("MB2", "Mut-Rule", 0.271, 3.40e-3, 0.031, 0.037),
    ("MB2", "RF",      0.079, 8.14e-6, 0.500, 0.240),
    ("MB2", "AE",      0.112, 1.90e-3, 0.022, 0.026),
    ("MB2", "TCAN",    0.000, 0.0,     0.000, 0.000),
    ("MB2", "MVT-RF",  0.143, 0.0,     1.000, 0.412),
    ("MB2", "Mut-RF",  0.000, 0.0,     0.000, 0.000),
]

df = pd.DataFrame(ROWS, columns=["model", "method", "TPR", "FPR", "Precision", "F0.5"])
df["method"] = pd.Categorical(df["method"], categories=METHODS, ordered=True)
df = df.sort_values(["model", "method"]).reset_index(drop=True)

def main():
    ensure_output_dirs()
    OUT_GRID_PDF = FIGURE_DIR / "chap3-baseline-bar-grid.pdf"

    METHOD_HATCHES = METHOD_HATCH

    GRID_METRICS = [
        ("TPR", "TPR", 1.0),
        ("FPR", r"FPR ($\times 10^{-5}$)", 1e5),
        ("Precision", "Precision", 1.0),
        ("F0.5", r"$F_{0.5}$", 1.0),
    ]

    # 单轴局部放大；上界可略高于末刻度，由 _ylim_with_headroom 留出头
    YLIM_GRID = {}
    YTICKS_GRID = {
        ("MB2", "TPR"): [0.0, 0.15, 0.30],
        ("MB2", "Precision"): [0.0, 0.5, 1.0],  # 末刻度=1，轴顶与之对齐
        ("MB2", "F0.5"): [0.0, 0.25, 0.5],
    }

    # 断轴：MB1 的 TPR / Precision / F0.5；MB1/MB2 的 FPR（Mut-Rule/AE 误报远高于学习型基线）
    # 上下段各 3 个刻度
    BROKEN_YLIM_GRID = {
        ("MB1", "TPR"): {
            "top": (0.73, 0.78),
            "bottom": (0.0, 0.08),
            "split": 0.08,
            "top_ticks": [0.73, 0.755, 0.78],
            "bottom_ticks": [0.0, 0.04, 0.08],
        },
        ("MB1", "Precision"): {
            "top": (0.92, 1.0),
            "bottom": (0.0, 0.60),
            "split": 0.60,
            "top_ticks": [0.92, 0.96, 1.0],
            "bottom_ticks": [0.0, 0.3, 0.6],
        },
        ("MB1", "F0.5"): {
            "top": (0.88, 0.92),
            "bottom": (0.0, 0.60),
            "split": 0.60,
            "top_ticks": [0.88, 0.90, 0.92],
            "bottom_ticks": [0.0, 0.3, 0.6],
        },
        ("MB1", "FPR"): {
            "top": (100.0, 140.0),
            "bottom": (0.0, 20.0),
            "split": 20.0,
            "top_ticks": [100, 115, 140],
            "bottom_ticks": [0, 10, 20],
        },
        ("MB2", "FPR"): {
            "top": (180.0, 340.0),
            "bottom": (0.0, 5.0),
            "split": 5.0,
            "top_ticks": [180, 260, 340],
            "bottom_ticks": [0, 2.5, 5],
        },
    }

    x = np.arange(len(METHODS))
    bar_width = 0.72
    # BREAK_GAP：断轴「上段柱 // 空白 // 下段柱」中间的空隙（figure 坐标）
    BREAK_GAP = 0.045
    BOT_FRAC = 0.30     # 下段高度占比（恢复原值）


    def _style_axis(ax):
        ax.grid(axis="y", alpha=0.30, linewidth=0.6, zorder=0)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", pad=2)


    TITLE_PAD = 10  # 指标标题与 MB1 行距（栏宽画布下收紧）


    def _draw_low_bar(ax, xi, v, raw, color, hatch, bot_lo, bot_hi):
        """下段：真实低值柱。"""
        if raw <= 0:
            return
        draw_v = min(max(v, bot_lo), bot_hi)
        if draw_v <= bot_lo:
            return
        bar = ax.bar(xi, draw_v - bot_lo, width=bar_width, bottom=bot_lo,
                     color=color, hatch=hatch, edgecolor=C_EDGE, linewidth=BAR_LW, zorder=3)
        if xi == 0:
            bar[0].set_linewidth(BAR_LW * 1.5)


    def _draw_bottom_fill(ax, xi, color, hatch, bot_lo, bot_hi):
        """下段：高值方法在短轴内画满（字典色/底纹原样）。"""
        span = bot_hi - bot_lo
        if span <= 0:
            return
        bar = ax.bar(xi, span, width=bar_width, bottom=bot_lo,
                     color=color, hatch=hatch, edgecolor=C_EDGE, linewidth=BAR_LW, zorder=3)
        if xi == 0:
            bar[0].set_linewidth(BAR_LW * 1.5)


    def _draw_top_bar(ax, xi, v, raw, color, hatch, top_lo, top_hi):
        """上段：放大区间内的真实柱。"""
        if raw <= 0 or v < top_lo:
            return
        draw_v = min(v, top_hi)
        bar = ax.bar(xi, draw_v - top_lo, width=bar_width, bottom=top_lo,
                     color=color, hatch=hatch, edgecolor=C_EDGE, linewidth=BAR_LW, zorder=3)
        if xi == 0:
            bar[0].set_linewidth(BAR_LW * 1.5)


    def _draw_break_marks(ax_top, ax_bot, d=0.018):
        kw = dict(color=C_ZERO, clip_on=False, linewidth=0.9)
        ax_top.plot((-d, +d), (-d, +d), transform=ax_top.transAxes, **kw)
        ax_top.plot((1 - d, 1 + d), (-d, +d), transform=ax_top.transAxes, **kw)
        ax_bot.plot((-d, +d), (1 - d, 1 + d), transform=ax_bot.transAxes, **kw)
        ax_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), transform=ax_bot.transAxes, **kw)
        ax_top.spines.bottom.set_visible(False)
        ax_bot.spines.top.set_visible(False)
        ax_top.tick_params(bottom=False, labelbottom=False)
        ax_bot.tick_params(top=False, labeltop=False)


    X_LIM = (-0.55, len(METHODS) - 0.45)


    def _apply_xlim(ax):
        ax.set_xlim(*X_LIM)
        ax.set_xticks(x)
        ax.set_xticklabels([])


    def _fmt_ytick(v, _):
        """刻度标签：整数不带小数；其余去掉末尾 0。"""
        if abs(v - round(v)) < 1e-9:
            return f"{int(round(v))}"
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s


    def _ylim_with_headroom(ylo, yhi, ticks, *, pad_frac=0.14):
        """末刻度非 1 时，轴顶略高出末刻度，避免「刻度封顶」；末刻度为 1 则贴齐。

        出头按「首末刻度跨度」比例计算（不用末刻度绝对值），否则断轴上段
        （如 0.89–0.93）会被 0.93 撑出过大空白，导致末刻度视觉上偏矮。
        """
        if not ticks:
            return ylo, yhi
        t_lo, t_hi = min(ticks), max(ticks)
        if abs(t_hi - 1.0) < 1e-9:
            return ylo, max(yhi, 1.0)
        span = max(t_hi - t_lo, 1e-9)
        return ylo, max(yhi, t_hi + pad_frac * span)


    def _set_yticks_sparse(ax, ylo, yhi, ticks=None):
        """普通子图统一约 3 个主刻度。"""
        if ticks is not None:
            ax.set_yticks(ticks)
        else:
            from matplotlib.ticker import MaxNLocator
            ax.yaxis.set_major_locator(MaxNLocator(nbins=3, min_n_ticks=3, prune=None))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(_fmt_ytick))


    def _align_broken_pair(ax_top, ax_bot):
        """上下段共享同一绘图区 left/width。"""
        _apply_xlim(ax_top)
        _apply_xlim(ax_bot)

        for ax in (ax_top, ax_bot):
            ax.yaxis.set_major_formatter(plt.FuncFormatter(_fmt_ytick))
            ax.yaxis.set_tick_params(pad=2, labelsize=FONT["note"])

        fig = ax_top.figure
        fig.canvas.draw()
        pos_t = ax_top.get_position()
        pos_b = ax_bot.get_position()
        ax_bot.set_position([pos_t.x0, pos_b.y0, pos_t.width, pos_b.height])



    def _draw_row_label(panel_col0, label):
        """行标签：整行垂直居中，置于第 0 列 y 刻度文字左侧。"""
        if panel_col0["kind"] == "broken":
            axes_ref = [panel_col0["bot"], panel_col0["top"]]
            fig = axes_ref[0].figure
            fig.canvas.draw()
            pb, pt = axes_ref[0].get_position(), axes_ref[1].get_position()
            y = 0.5 * (
                (pb.y0 + 0.5 * pb.height) + (pt.y0 + 0.5 * pt.height)
            )
        else:
            axes_ref = [panel_col0["ax"]]
            fig = axes_ref[0].figure
            fig.canvas.draw()
            pos = axes_ref[0].get_position()
            y = pos.y0 + 0.5 * pos.height

        renderer = fig.canvas.get_renderer()
        inv = fig.transFigure.inverted()
        # 取该列所有 y 刻度标签的最左缘，再向左留空隙
        tick_left = min(ax.get_position().x0 for ax in axes_ref)
        for ax in axes_ref:
            for t in ax.get_yticklabels():
                if not t.get_visible() or not t.get_text():
                    continue
                bb = t.get_window_extent(renderer).transformed(inv)
                tick_left = min(tick_left, bb.x0)

        fig.text(
            tick_left - 0.032, y, label,
            transform=fig.transFigure,
            rotation=90, va="center", ha="center",
            fontsize=FONT["title"], fontweight="bold",
            clip_on=False,
        )


    def _plot_broken_panel(fig, ax_placeholder, *, raw_vals, vals, colors, hatches, cfg, ylabel, key,
                           show_title=False, show_model_label=False):
        pos = ax_placeholder.get_position()
        ax_placeholder.remove()

        bot_h = pos.height * BOT_FRAC
        top_h = pos.height - bot_h - BREAK_GAP
        ax_top = fig.add_axes([pos.x0, pos.y0 + bot_h + BREAK_GAP, pos.width, top_h])
        ax_bot = fig.add_axes([pos.x0, pos.y0, pos.width, bot_h], sharex=ax_top)

        top_lo, top_hi = cfg["top"]
        bot_lo, bot_hi = cfg["bottom"]
        split = cfg.get("split", bot_hi)  # 截断阈值：与 bottom 上界对齐，独立于 top 放大区间

        for xi, v, raw, c, h in zip(x, vals, raw_vals, colors, hatches):
            if raw <= 0:
                continue
            if v >= split:
                _draw_bottom_fill(ax_bot, xi, c, h, bot_lo, bot_hi)
            else:
                _draw_low_bar(ax_bot, xi, v, raw, c, h, bot_lo, bot_hi)
            if v >= top_lo:
                _draw_top_bar(ax_top, xi, v, raw, c, h, top_lo, top_hi)

        # 上段出头需可辨认（过小看不出）；随后与 FPR 末刻度水平对齐
        ax_top.set_ylim(*_ylim_with_headroom(top_lo, top_hi, cfg["top_ticks"], pad_frac=0.10))
        ax_bot.set_ylim(*_ylim_with_headroom(bot_lo, bot_hi, cfg["bottom_ticks"], pad_frac=0.14))
        ax_top.set_yticks(cfg["top_ticks"])
        ax_bot.set_yticks(cfg["bottom_ticks"])
        _style_axis(ax_top)
        _style_axis(ax_bot)
        _draw_break_marks(ax_top, ax_bot)

        # 指标含义统一放在列标题，不设 y 轴文字标签（避免与 MB 行标签抢位）
        if show_title:
            ax_top.set_title(ylabel, fontweight="bold", pad=TITLE_PAD)

        ax_top.set_xticks(x)
        ax_top.set_xticklabels([])
        ax_bot.set_xticks(x)
        ax_bot.set_xticklabels([])
        _align_broken_pair(ax_top, ax_bot)
        return ax_top, ax_bot


    def _last_ytick(ax):
        ylo, yhi = ax.get_ylim()
        ticks = [t for t in ax.get_yticks() if ylo - 1e-9 <= t <= yhi + 1e-9]
        return max(ticks) if ticks else None


    def _last_ytick_fig_y(ax):
        """末刻度在 figure 坐标中的垂直位置。"""
        pos = ax.get_position()
        ylo, yhi = ax.get_ylim()
        t = _last_ytick(ax)
        if t is None or yhi <= ylo:
            return None
        return pos.y0 + (t - ylo) / (yhi - ylo) * pos.height


    def _set_ylim_to_match_last_tick_fig_y(ax, fig_y):
        """调整 y 上界，使末刻度落在给定 figure-y（末刻度为 1 的贴顶轴不改）。"""
        pos = ax.get_position()
        ylo, yhi = ax.get_ylim()
        t = _last_ytick(ax)
        if t is None or abs(t - 1.0) < 1e-9:
            return
        target_frac = (fig_y - pos.y0) / max(pos.height, 1e-9)
        target_frac = float(np.clip(target_frac, 0.05, 0.995))
        ax.set_ylim(ylo, ylo + (t - ylo) / target_frac)


    def _align_row_last_ticks(panels, fig):
        """同行各面板末刻度水平对齐（含单轴与断轴上段；末刻度=1 的贴顶轴不改）。

        MB2：对齐 TPR 0.3、FPR 360、$F_{0.5}$ 0.6；Precision 末刻度=1 跳过。
        """
        fig.canvas.draw()
        axes = []
        for p in panels:
            ax = p["top"] if p["kind"] == "broken" else p["ax"]
            t = _last_ytick(ax)
            if t is not None and abs(t - 1.0) > 1e-9:
                axes.append(ax)
        if len(axes) < 2:
            return
        ys = [_last_ytick_fig_y(ax) for ax in axes]
        if any(y is None for y in ys):
            return
        target = sum(ys) / len(ys)
        for ax in axes:
            _set_ylim_to_match_last_tick_fig_y(ax, target)


    def _place_panel(panel, x0, y0, w, h):
        """将简单/断轴面板放入同一单元格（断轴内 BOT_FRAC + BREAK_GAP）。"""
        if panel["kind"] == "broken":
            bot_h = h * BOT_FRAC
            top_h = h - bot_h - BREAK_GAP
            panel["bot"].set_position([x0, y0, w, bot_h])
            panel["top"].set_position([x0, y0 + bot_h + BREAK_GAP, w, top_h])
            _align_broken_pair(panel["top"], panel["bot"])
        else:
            _apply_xlim(panel["ax"])
            panel["ax"].set_position([x0, y0, w, h])


    def _layout_equal_grid(row_panels, *, left, right, top, bottom, wspace, hspace):
        """四列等宽、列间距均分；两行等高，FPR 与其余列共用同一单元格高度。

        断轴用 fig.add_axes 创建后不会随 subplots_adjust 移动，必须在此统一落位。
        """
        n_cols = len(row_panels[0])
        n_rows = len(row_panels)
        avail_w = right - left
        avail_h = top - bottom
        # 与 matplotlib wspace/hspace 定义一致：间隙 = 系数 × 平均轴宽/高
        col_w = avail_w / (n_cols + (n_cols - 1) * wspace)
        col_gap = wspace * col_w
        row_h = avail_h / (n_rows + (n_rows - 1) * hspace)
        row_gap = hspace * row_h
        y0s = [bottom + (n_rows - 1 - r) * (row_h + row_gap) for r in range(n_rows)]

        for col in range(n_cols):
            x0 = left + col * (col_w + col_gap)
            for row in range(n_rows):
                _place_panel(row_panels[row][col], x0, y0s[row], col_w, row_h)


    def _plot_simple_panel(ax, *, vals, colors, hatches, ylabel, key, model,
                           show_title=False, show_model_label=False):
        custom_ylim = YLIM_GRID.get((model, key))
        if custom_ylim is not None:
            ylo, yhi = custom_ylim
        else:
            ylo = 0.0
            if vals.max() > 0:
                yhi = max(vals.max() * 1.22, 0.08)
                if key in ("TPR", "Precision", "F0.5"):
                    yhi = min(yhi, 1.0)
            else:
                yhi = 1.0

        bars = ax.bar(x, vals, width=bar_width, color=colors, hatch=hatches,
                      edgecolor=C_EDGE, linewidth=BAR_LW, zorder=3)
        bars[0].set_linewidth(BAR_LW * 1.5)
        ticks = YTICKS_GRID.get((model, key))
        ylo, yhi = _ylim_with_headroom(ylo, yhi, ticks)
        ax.set_ylim(ylo, yhi)
        _set_yticks_sparse(ax, ylo, yhi, ticks=ticks)
        _style_axis(ax)
        if show_title:
            # FPR 保留 ×10^{-5} 于列标题；其余指标名同 ylabel
            ax.set_title(ylabel, fontweight="bold", pad=TITLE_PAD)
        _apply_xlim(ax)
        return ax


    # 按版心宽度出图：正文 \\includegraphics 默认尺寸即可，避免 width= 缩放缩字号
    fig, axes = plt.subplots(2, 4, figsize=(TEXT_WIDTH_IN, 3.55), sharex=False)

    broken_pairs = []
    row_panels = [[], []]

    for row, model in enumerate(MODELS):
        sub = df[df["model"] == model].set_index("method").loc[METHODS]
        for col, (key, ylabel, scale) in enumerate(GRID_METRICS):
            ax = axes[row, col]
            raw_vals = sub[key].to_numpy(dtype=float)
            vals = raw_vals * scale
            colors = [METHOD_COLORS[m] for m in METHODS]
            hatches = [METHOD_HATCHES[m] for m in METHODS]
            broken_cfg = BROKEN_YLIM_GRID.get((model, key))

            if broken_cfg is not None:
                ax_top, ax_bot = _plot_broken_panel(
                    fig, ax,
                    raw_vals=raw_vals, vals=vals, colors=colors, hatches=hatches,
                    cfg=broken_cfg, ylabel=ylabel, key=key,
                    show_title=(row == 0),
                    show_model_label=(col == 0),
                )
                broken_pairs.append((ax_top, ax_bot))
                row_panels[row].append({"kind": "broken", "top": ax_top, "bot": ax_bot})
                axes[row, col] = ax_bot
            else:
                _plot_simple_panel(
                    ax, vals=vals, colors=colors, hatches=hatches,
                    ylabel=ylabel, key=key, model=model,
                    show_title=(row == 0),
                    show_model_label=(col == 0),
                )
                row_panels[row].append({"kind": "simple", "ax": ax})

    # 底部不显示方法名（避免与图例/断轴下段重叠），方法见底部图例
    for row in range(2):
        for col in range(4):
            _apply_xlim(axes[row, col])
    for _, ax_bot in broken_pairs:
        _apply_xlim(ax_bot)

    legend_handles = [
        Patch(facecolor=METHOD_COLORS[m], hatch=METHOD_HATCHES[m],
              edgecolor=C_EDGE, linewidth=BAR_LW, label=m)
        for m in METHODS
    ]

    # 断轴面板不随 subplots_adjust 移动：用等宽列 + 等高行统一落位
    LAYOUT = dict(left=0.15, right=0.99, top=0.88, bottom=0.14, wspace=0.38, hspace=0.28)
    fig.subplots_adjust(**LAYOUT)
    _layout_equal_grid(row_panels, **LAYOUT)
    _align_row_last_ticks(row_panels[0], fig)  # MB1
    _align_row_last_ticks(row_panels[1], fig)  # MB2：TPR/FPR/F0.5 末刻度水平对齐
    _draw_row_label(row_panels[0][0], "MB1")
    _draw_row_label(row_panels[1][0], "MB2")

    # 布局定稿后再放共享图例（统一样式 +「图例」整体居中）
    fig_shared_legend(
        fig,
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=7,
        columnspacing=0.55,
        handletextpad=0.30,
        borderpad=0.3,
    )

    savefig_text_width(fig, OUT_GRID_PDF, pad_inches=0.02)
    print(f"saved: {OUT_GRID_PDF}")


if __name__ == "__main__":
    main()
