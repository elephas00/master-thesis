"""第三章：盘级基线对比 2×4 分组柱图（方案 4）

对应 notebook `codes/eda/notebooks/eda_baseline_bar_chart.ipynb` §4。
生成 figure/chap3-baseline-bar-grid.png 与同名 .pdf。

用法（项目根目录）:
    python figure_codes/chap3_baseline_bar_grid.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.transforms import blended_transform_factory

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
})

METHODS = ["本文方法", "RF", "AE", "TCAN", "MVT-RF", "Mut-RF"]
MODELS = ["MB1", "MB2"]

# 三轮平均（与 content.tex 主结果表一致）
ROWS = [
    # model, method, TPR, FPR, Precision, F0.5
    ("MB1", "本文方法", 0.738, 2.71e-5, 0.981, 0.921),
    ("MB1", "RF",      0.765, 1.18e-4, 0.935, 0.895),
    ("MB1", "AE",      0.038, 1.34e-3, 0.043, 0.042),
    ("MB1", "TCAN",    0.000, 0.0,     0.000, 0.000),
    ("MB1", "MVT-RF",  0.769, 4.53e-5, 0.967, 0.919),
    ("MB1", "Mut-RF",  0.020, 3.63e-5, 0.500, 0.086),
    ("MB2", "本文方法", 0.187, 0.0,     1.000, 0.490),
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
    OUT_GRID = FIGURE_DIR / "chap3-baseline-bar-grid.png"
    OUT_GRID_PDF = FIGURE_DIR / "chap3-baseline-bar-grid.pdf"

    METHOD_COLORS = {
        "本文方法": "#2563EB",
        "RF": "#DC2626",
        "AE": "#F59E0B",
        "TCAN": "#6B7280",
        "MVT-RF": "#16A34A",
        "Mut-RF": "#9333EA",
    }

    GRID_METRICS = [
        ("TPR", "TPR", 1.0, "{:.3f}"),
        ("FPR", r"FPR ($\times 10^{-5}$)", 1e5, "{:.2e}"),
        ("Precision", "Precision", 1.0, "{:.3f}"),
        ("F0.5", r"$F_{0.5}$", 1.0, "{:.3f}"),
    ]

    # 单轴局部放大（FPR 等）
    YLIM_GRID = {
        ("MB1", "FPR"): (0.0, 25.0),
        ("MB2", "FPR"): (0.0, 10.0),
    }

    # MB1 TPR / Precision / F0.5：断轴
    # - top / bottom：上下段 y 轴显示范围（放大区间 vs 0 附近密集刻度区）
    # - split：截断阈值（默认 = bottom 上界）；v >= split → 下段画延续柱；v >= top[0] → 上段画真实柱
    BROKEN_YLIM_GRID = {
        ("MB1", "TPR"): {
            "top": (0.73, 0.78),
            "bottom": (0.0, 0.08),
            "split": 0.08,
            "top_ticks": np.arange(0.73, 0.785, 0.01),
            "bottom_ticks": [0.0, 0.02, 0.04, 0.06, 0.08],
        },
        ("MB1", "Precision"): {
            "top": (0.93, 0.98),
            "bottom": (0.0, 0.55),
            "split": 0.55,
            "top_ticks": np.arange(0.93, 0.985, 0.01),
            "bottom_ticks": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        },
        ("MB1", "F0.5"): {
            "top": (0.89, 0.93),
            "bottom": (0.0, 0.12),
            "split": 0.12,
            "top_ticks": np.arange(0.89, 0.935, 0.01),
            "bottom_ticks": [0.0, 0.04, 0.08, 0.12],
        },
    }

    x = np.arange(len(METHODS))
    bar_width = 0.72
    BREAK_GAP = 0.028   # 上下段间距，避免刻度/标注重叠
    BOT_FRAC = 0.26     # 下段高度占比


    def _style_axis(ax):
        ax.grid(axis="y", alpha=0.30, linewidth=0.6, zorder=0)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", pad=2)


    def _annotate_zero(ax, xi, ylo, yhi, color):
        """指标为 0：在 y 轴下沿标注「0」，不绘制柱形。"""
        span = max(yhi - ylo, 1e-9)
        y = ylo + 0.035 * span
        ax.plot([xi, xi], [ylo, ylo + 0.018 * span], color=color, lw=0.9, zorder=4, alpha=0.9)
        ax.text(xi, y, "0", ha="center", va="bottom", fontsize=6.5,
                color=color, zorder=5, alpha=0.95)


    TITLE_PAD = 12  # 列标题与子图之间的间距


    def _annotate_bar(ax, xi, v, raw, fmt, key, ylo, yhi, *, rotation=0, above_bar=False):
        if raw <= 0:
            return
        span = max(yhi - ylo, 1e-9)
        label = fmt.format(raw if key != "FPR" else raw)
        if above_bar:
            bar_top = min(max(v, ylo), yhi)
            y_text = bar_top + 0.015 * span
            ax.text(xi, y_text, label, ha="center", va="bottom",
                    fontsize=6.0, rotation=rotation, zorder=5, clip_on=False)
            return
        if v > yhi:
            ax.text(xi, yhi - 0.05 * span, label, ha="center", va="top",
                    fontsize=6.0, rotation=rotation, zorder=4, color="#7F1D1D")
            return
        if v < ylo:
            return
        ax.text(xi, min(v + 0.03 * span, yhi - 0.01 * span), label,
                ha="center", va="bottom", fontsize=6.0, rotation=rotation, zorder=4)


    def _draw_low_bar(ax, xi, v, raw, color, bot_lo, bot_hi, fmt, key):
        """下段：真实低值柱 + 数值标注。"""
        if raw <= 0:
            return
        draw_v = min(max(v, bot_lo), bot_hi)
        if draw_v <= bot_lo:
            return
        bar = ax.bar(xi, draw_v - bot_lo, width=bar_width, bottom=bot_lo,
                     color=color, edgecolor="#0F172A", linewidth=0.6, zorder=3)
        if xi == 0:
            bar[0].set_linewidth(1.8)
        _annotate_bar(ax, xi, draw_v, raw, fmt, key, bot_lo, bot_hi)


    def _draw_continuation_stub(ax, xi, color, bot_lo, bot_hi):
        """下段：高值方法画到顶部的截断柱，表示向上延续（省略区上方还有该方法的柱）。"""
        span = bot_hi - bot_lo
        bar = ax.bar(xi, span, width=bar_width, bottom=bot_lo,
                     color=color, edgecolor="#0F172A", linewidth=0.6,
                     hatch="///", alpha=0.92, zorder=3)
        if xi == 0:
            bar[0].set_linewidth(1.8)
        # 柱顶小三角，提示向上延续
        cx = xi
        tri_h = span * 0.10
        ax.plot([cx, cx - bar_width * 0.18, cx + bar_width * 0.18],
                [bot_hi, bot_hi - tri_h, bot_hi - tri_h],
                color="#0F172A", lw=0.8, zorder=4, clip_on=True)


    def _draw_top_bar(ax, xi, v, raw, color, top_lo, top_hi, fmt, key):
        """上段：放大区间内的真实柱 + 数值标注。"""
        if raw <= 0 or v < top_lo:
            return
        draw_v = min(v, top_hi)
        bar = ax.bar(xi, draw_v - top_lo, width=bar_width, bottom=top_lo,
                     color=color, edgecolor="#0F172A", linewidth=0.6, zorder=3)
        if xi == 0:
            bar[0].set_linewidth(1.8)
        _annotate_bar(ax, xi, draw_v, raw, fmt, key, top_lo, top_hi)


    def _draw_break_marks(ax_top, ax_bot, d=0.018):
        kw = dict(color="#334155", clip_on=False, linewidth=0.9)
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


    def _align_broken_pair(ax_top, ax_bot):
        """上下段共享同一绘图区 left/width。"""
        _apply_xlim(ax_top)
        _apply_xlim(ax_bot)

        ylabel_text = ax_top.yaxis.get_label().get_text()
        if ylabel_text:
            ax_bot.set_ylabel(ylabel_text, labelpad=2)
            ax_bot.yaxis.label.set_visible(False)

        for ax in (ax_top, ax_bot):
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}"))
            ax.yaxis.set_tick_params(pad=3)

        fig = ax_top.figure
        fig.canvas.draw()
        pos_t = ax_top.get_position()
        pos_b = ax_bot.get_position()
        ax_bot.set_position([pos_t.x0, pos_b.y0, pos_t.width, pos_b.height])



    def _draw_row_label(panel_col0, label):
        """行标签：x 位置与 MB2 列0 一致（transAxes -0.28），y 为整列垂直居中。"""
        if panel_col0["kind"] == "broken":
            ax_ref = panel_col0["bot"]
            ax_top = panel_col0["top"]
            fig = ax_ref.figure
            fig.canvas.draw()
            pb, pt = ax_ref.get_position(), ax_top.get_position()
            y_center = pb.y0 + 0.5 * (pt.y0 + pt.height - pb.y0)
            trans = blended_transform_factory(ax_ref.transAxes, fig.transFigure)
            ax_ref.text(
                -0.28, y_center, label, transform=trans,
                rotation=90, va="center", ha="center", fontsize=12, fontweight="bold",
            )
        else:
            ax = panel_col0["ax"]
            ax.text(
                -0.28, 0.5, label, transform=ax.transAxes,
                rotation=90, va="center", ha="center", fontsize=12, fontweight="bold",
            )


    def _plot_broken_panel(fig, ax_placeholder, *, raw_vals, vals, colors, cfg, ylabel, fmt, key,
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

        for xi, v, raw, c in zip(x, vals, raw_vals, colors):
            if raw <= 0:
                _annotate_zero(ax_bot, xi, bot_lo, bot_hi, c)
                continue
            if v >= split:
                _draw_continuation_stub(ax_bot, xi, c, bot_lo, bot_hi)
            else:
                _draw_low_bar(ax_bot, xi, v, raw, c, bot_lo, bot_hi, fmt, key)
            if v >= top_lo:
                _draw_top_bar(ax_top, xi, v, raw, c, top_lo, top_hi, fmt, key)

        ax_top.set_ylim(top_lo, top_hi)
        ax_bot.set_ylim(bot_lo, bot_hi)
        ax_top.set_yticks(cfg["top_ticks"])
        ax_bot.set_yticks(cfg["bottom_ticks"])
        _style_axis(ax_top)
        _style_axis(ax_bot)
        _draw_break_marks(ax_top, ax_bot)

        ax_top.set_ylabel(ylabel, labelpad=2)
        if show_title:
            ax_top.set_title(ylabel, fontweight="bold", pad=TITLE_PAD)

        ax_top.set_xticks(x)
        ax_top.set_xticklabels([])
        ax_bot.set_xticks(x)
        ax_bot.set_xticklabels([])
        _align_broken_pair(ax_top, ax_bot)
        return ax_top, ax_bot


    def _panel_bbox(ax_top, ax_bot):
        """断轴子图整体外框（上段顶 → 下段底）。"""
        fig = ax_top.figure
        fig.canvas.draw()
        pt, pb = ax_top.get_position(), ax_bot.get_position()
        return pt.x0, pb.y0, pt.width, pt.y0 + pt.height - pb.y0


    def _broken_column_span(panel):
        """断轴列整列 bbox：bottom y0 与总高度（含 BREAK_GAP）。"""
        pb, pt = panel["bot"].get_position(), panel["top"].get_position()
        return pb.y0, pt.y0 + pt.height - pb.y0


    def _plot_left_inset(ax, fig):
        """绘图区左缘相对 axes bbox 的偏移（figure 坐标）。"""
        renderer = fig.canvas.get_renderer()
        ax_pos = ax.get_position()
        spine_x = ax.spines["left"].get_window_extent(renderer).transformed(fig.transFigure.inverted()).x0
        return spine_x - ax_pos.x0


    def _align_plot_left_margin(ax_target, ax_ref, fig, x0_col, y0, h, w_col):
        """对齐绘图区左缘边距，使 x 轴刻度与断轴列一致。"""
        ax_target.set_position([x0_col, y0, w_col, h])
        fig.canvas.draw()
        delta = _plot_left_inset(ax_ref, fig) - _plot_left_inset(ax_target, fig)
        ax_target.set_position([x0_col + delta, y0, w_col - delta, h])


    def _align_mb1_columns_to_mb2(mb1_panels, mb2_panels, fig):
        """以 MB2 各列为基准，对齐 MB1 同指标列的 x0 / width / height。"""
        fig.canvas.draw()
        mb1_row_span = None
        mb1_broken_ref = None

        for p1, p2 in zip(mb1_panels, mb2_panels):
            if p2["kind"] != "simple":
                continue
            pos2 = p2["ax"].get_position()
            x0, w, h_ref = pos2.x0, pos2.width, pos2.height

            if p1["kind"] == "broken":
                y0 = p1["bot"].get_position().y0
                bot_h = h_ref * BOT_FRAC
                top_h = h_ref - bot_h - BREAK_GAP
                p1["bot"].set_position([x0, y0, w, bot_h])
                p1["top"].set_position([x0, y0 + bot_h + BREAK_GAP, w, top_h])
                _align_broken_pair(p1["top"], p1["bot"])
                if mb1_row_span is None:
                    fig.canvas.draw()
                    mb1_row_span = _broken_column_span(p1)
                    mb1_broken_ref = p1["bot"]
            else:
                if mb1_row_span is None:
                    ref = next(p for p in mb1_panels if p["kind"] == "broken")
                    fig.canvas.draw()
                    mb1_row_span = _broken_column_span(ref)
                    mb1_broken_ref = ref["bot"]
                y0_col, h_col = mb1_row_span
                _apply_xlim(p1["ax"])
                _align_plot_left_margin(p1["ax"], mb1_broken_ref, fig, x0, y0_col, h_col, w)


    def _plot_simple_panel(ax, *, raw_vals, vals, colors, ylabel, fmt, key, model,
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

        bars = ax.bar(x, vals, width=bar_width, color=colors,
                      edgecolor="#0F172A", linewidth=0.6, zorder=3)
        bars[0].set_linewidth(1.8)
        ax.set_ylim(ylo, yhi)
        if model == "MB1" and key == "FPR":
            ax.set_ylabel("FPR", labelpad=2)
        else:
            ax.set_ylabel(ylabel)
        _style_axis(ax)
        if show_title:
            ax.set_title(ylabel.replace(r" ($\times 10^{-5}$)", ""), fontweight="bold", pad=TITLE_PAD)
        for xi, v, raw, c in zip(x, vals, raw_vals, colors):
            if raw <= 0:
                _annotate_zero(ax, xi, ylo, yhi, c)
                continue
            _annotate_bar(ax, xi, v, raw, fmt, key, ylo, yhi, above_bar=(key == "FPR"))
        _apply_xlim(ax)
        return ax


    fig, axes = plt.subplots(2, 4, figsize=(13.8, 7.4), sharex=False)

    broken_pairs = []
    row_panels = [[], []]

    for row, model in enumerate(MODELS):
        sub = df[df["model"] == model].set_index("method").loc[METHODS]
        for col, (key, ylabel, scale, fmt) in enumerate(GRID_METRICS):
            ax = axes[row, col]
            raw_vals = sub[key].to_numpy(dtype=float)
            vals = raw_vals * scale
            colors = [METHOD_COLORS[m] for m in METHODS]
            broken_cfg = BROKEN_YLIM_GRID.get((model, key))

            if broken_cfg is not None:
                ax_top, ax_bot = _plot_broken_panel(
                    fig, ax,
                    raw_vals=raw_vals, vals=vals, colors=colors,
                    cfg=broken_cfg, ylabel=ylabel, fmt=fmt, key=key,
                    show_title=(row == 0),
                    show_model_label=(col == 0),
                )
                broken_pairs.append((ax_top, ax_bot))
                row_panels[row].append({"kind": "broken", "top": ax_top, "bot": ax_bot})
                axes[row, col] = ax_bot
            else:
                _plot_simple_panel(
                    ax, raw_vals=raw_vals, vals=vals, colors=colors,
                    ylabel=ylabel, fmt=fmt, key=key, model=model,
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

    legend_handles = [Patch(facecolor=METHOD_COLORS[m], edgecolor="#0F172A", label=m) for m in METHODS]
    fig.legend(
        handles=legend_handles, loc="lower center", ncol=6,
        framealpha=0.95, edgecolor="#CBD5E1", bbox_to_anchor=(0.5, -0.01), fontsize=9,
    )

    fig.subplots_adjust(left=0.08, right=0.98, top=0.96, bottom=0.14, wspace=0.42, hspace=0.62)

    for ax_top, ax_bot in broken_pairs:
        _align_broken_pair(ax_top, ax_bot)
    _align_mb1_columns_to_mb2(row_panels[0], row_panels[1], fig)
    _draw_row_label(row_panels[0][0], "MB1")
    _draw_row_label(row_panels[1][0], "MB2")
    # fig.savefig(OUT_GRID, bbox_inches="tight")
    fig.savefig(OUT_GRID_PDF, bbox_inches="tight")
    print(f"saved: {OUT_GRID}")
    print(f"saved: {OUT_GRID_PDF}")


if __name__ == "__main__":
    main()
