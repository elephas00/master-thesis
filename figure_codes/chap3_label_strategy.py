"""第三章：五种标记策略对比示意

生成 figure/chap3-label-strategy.pdf。

横轴为示意天数（非真实日历），仅保持相对位置：
近端 d=1,2,3 更易辨认，远端首跳压缩。

用法（项目根目录）:
    python figure_codes/chap3_label_strategy.py
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "font.size": 11,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# ---------- 示意参数（线性坐标，等比缩小远端） ----------
# 对应关系：W≈30日窗, K_SHORT=3, 窗外首跳≈35, 较早首跳≈15
W = 10
K_SHORT = 3
K_LONG = W
RECORD_EXT = 4
RECORD_LEFT = W + RECORD_EXT

DISKS = [
    ("近端首跳（1日）", 2),
    ("近端首跳（0日）", 1),
    ("静默", None),
    ("窗内首跳", 6),
    ("首跳在观测窗外", 11),
]

STRATEGIES = [
    ("fix_long", "固定长窗"),
    ("fix_short", "固定短窗"),
    ("fix_day", "故障当日"),
    ("jump", "首跳窗口"),
    ("mix", "混合（本文）"),
]

COLORS = {
    "correct": "#70AD47",
    "wrong_fc": "#FFCDD2",
    "wrong_ec": "#E57373",
    "record_hist": "#ECECEC",
    "record_win": "#F5F5F5",
    "track_edge": "#D0D0D0",
    "fail": "#37474F",
    "warn_line": "#78909C",
    "jump_mk": "#1565C0",
}

BAR_H = 0.13
OUTPUT_PDF = FIGURE_DIR / "chap3-label-strategy.pdf"


def _rect(ax, d_left, d_right, y, h, **kwargs):
    ax.add_patch(mpatches.Rectangle((d_right, y - h / 2), d_left - d_right, h, **kwargs))


def _obs_jump(d_jump, w=W):
    if d_jump is None or d_jump > w:
        return None
    return d_jump


def _resolve_strategy(strategy, k_short=K_SHORT):
    if strategy == "fix_day":
        return "fix_short", 0
    return strategy, k_short


def _label_segments(strategy, d_jump, w=W, k_short=K_SHORT, k_long=K_LONG):
    strategy, k_short = _resolve_strategy(strategy, k_short)

    if d_jump is not None and d_jump > w:
        if strategy == "fix_long":
            return w, []
        if strategy == "fix_short":
            return k_short, []
        if strategy == "jump":
            return w, [(d_jump, w)]
        if strategy == "mix":
            return k_short, []

    if d_jump is None:
        if strategy == "fix_long":
            return None, [(w, 0)]
        if strategy == "fix_short":
            # k=0 静默：故障日标正但无跳变前兆，视为无效标注（示意宽度 1 日）
            if k_short == 0:
                return None, [(1, 0)]
            return None, [(k_short, 0)]
        return None, []

    if strategy in ("fix_long", "fix_short"):
        if strategy == "fix_long":
            fix_end = w
            valid_left = d_jump
        else:
            fix_end = k_short
            valid_left = min(d_jump, k_short)
        invalid = [(fix_end, valid_left)] if fix_end > valid_left else []
        return valid_left, invalid
    if strategy == "jump":
        return d_jump, []
    if strategy == "mix":
        return min(_obs_jump(d_jump, w), k_short) if _obs_jump(d_jump, w) else None, []

    raise ValueError(strategy)


def _display_valid_left(valid_left, k_short):
    # k=0 时有效区间退化为故障日单日，示意宽度与 k=3 中「一日」等宽
    if k_short == 0 and valid_left == 0:
        return 1
    return valid_left


def _display_invalid_seg(d_left, d_right, k_short):
    if k_short == 0 and d_left == d_right:
        return 1, 0
    return d_left, d_right


def _draw_labels(ax, y, strategy, d_jump, h=BAR_H, k_short=K_SHORT):
    strategy, k_short = _resolve_strategy(strategy, k_short)
    valid_left, invalid_segs = _label_segments(strategy, d_jump, k_short=k_short)
    if valid_left is not None:
        _rect(
            ax, _display_valid_left(valid_left, k_short), 0, y, h,
            facecolor=COLORS["correct"],
            edgecolor="#548235",
            linewidth=0.5,
            zorder=3,
        )
    for d_left, d_right in invalid_segs:
        d_left, d_right = _display_invalid_seg(d_left, d_right, k_short)
        if d_left <= d_right:
            continue
        k0_invalid = k_short == 0
        _rect(
            ax, d_left, d_right, y, h,
            facecolor=COLORS["wrong_fc"],
            edgecolor=COLORS["wrong_ec"],
            hatch="///",
            alpha=1.0 if k0_invalid else 0.75,
            linewidth=0.8 if k0_invalid else 0.5,
            zorder=4 if k0_invalid else 2,
        )


def _disk_ys(n):
    step = 1.0 / (n + 1)
    return [1.0 - (i + 1) * step for i in range(n)]


def _draw_record(ax, y, record_left=RECORD_LEFT, w=W, h=BAR_H):
    _rect(ax, record_left, w, y, h, facecolor=COLORS["record_hist"], edgecolor="none", zorder=1)
    _rect(
        ax, w, 0, y, h,
        facecolor=COLORS["record_win"],
        edgecolor=COLORS["track_edge"],
        linewidth=0.5,
        zorder=1,
    )


def plot_label_strategy(disks=DISKS, strategies=STRATEGIES, w=W, record_left=RECORD_LEFT):
    n_cols = len(strategies)
    ys = _disk_ys(len(disks))
    plot_left = record_left + 1.0

    fig, axes = plt.subplots(1, n_cols, figsize=(2.2 * n_cols + 0.5, 4.0), sharex=True)
    if n_cols == 1:
        axes = [axes]

    for c, (key, title) in enumerate(strategies):
        ax = axes[c]
        ax.set_xlim(plot_left, -0.5)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_title(title, fontsize=9.5, pad=10)
        for spine in ("left", "top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color("#BDBDBD")

        for y, (_, d_jump) in zip(ys, disks):
            _draw_record(ax, y, record_left, w)
            _draw_labels(ax, y, key, d_jump)
            if d_jump is not None:
                ax.plot(
                    d_jump, y + BAR_H / 2 + 0.02,
                    marker="v", ms=5.5,
                    color=COLORS["jump_mk"],
                    clip_on=False,
                    zorder=4,
                )

        ax.axvline(0, color=COLORS["fail"], lw=1.6, zorder=5)
        ax.axvline(w, color=COLORS["warn_line"], ls="--", lw=1.2, alpha=0.85, zorder=6)
        if key != "fix_day":
            ax.axvline(K_SHORT, color="#BDBDBD", ls=":", lw=0.7, zorder=0, alpha=0.7)

        if c == 0:
            for y, (disk_label, _) in zip(ys, disks):
                ax.text(
                    -0.06, y, disk_label,
                    transform=ax.transAxes,
                    ha="right", va="center",
                    fontsize=8.0, color="#424242",
                )

    # fig.suptitle(
    #     "不同标签策略示意图",
    #     y=0.02,
    #     fontsize=11,
    #     fontweight="bold",
    #     ha="center",
    #     color="#212121",
    # )
    for ax in axes:
        ax.set_xticks([0])
        ax.set_xticklabels(["$t_{\\mathrm{fail}}$"])
        ax.set_xlabel("")

    legend_handles = [
        mpatches.Patch(
            facecolor=COLORS["record_hist"], edgecolor=COLORS["track_edge"],
            label="观测记录",
        ),
        mpatches.Patch(
            facecolor=COLORS["correct"], edgecolor="#548235",
            label="有效标注",
        ),
        mpatches.Patch(
            facecolor=COLORS["wrong_fc"], edgecolor=COLORS["wrong_ec"],
            hatch="///", alpha=0.75,
            label="无效标注",
        ),
        Line2D(
            [0], [0], color=COLORS["warn_line"], ls="--", lw=1.2,
            label="预警观测窗左界",
        ),
        Line2D(
            [0], [0], marker="v", color="w", label="首跳时刻",
            markerfacecolor=COLORS["jump_mk"], markeredgecolor=COLORS["jump_mk"],
            markersize=6, markeredgewidth=0, linestyle="None",
        ),
    ]
    fig.legend(
        handles=legend_handles, loc="upper center", ncol=5,
        bbox_to_anchor=(0.5, 1.02), frameon=False, fontsize=8.5,
        handlelength=1.0, handletextpad=0.35, columnspacing=0.9,
    )

    fig.subplots_adjust(left=0.15, right=0.99, top=0.84, bottom=0.18, wspace=0.32)
    return fig


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot_label_strategy()
    fig.savefig(OUTPUT_PDF, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
