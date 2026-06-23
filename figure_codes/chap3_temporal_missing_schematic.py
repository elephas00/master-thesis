"""第三章：日历级缺失补全/剔除示意

生成 figure/temporal-missing-schematic.png。

三行子图分别示意轻度、中度、重度缺失下 40 日历日内的
有日志 / 待补全 / 整盘删除 三种状态（非真实盘数据）。

用法（项目根目录）:
    python figure_codes/chap3_temporal_missing_schematic.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUTPUT_PNG = FIGURE_DIR / "temporal-missing-schematic.png"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
})


def plot_timeline_schematic(output: Path = OUTPUT_PNG) -> plt.Figure:
    """示意：40 日历日内轻度/中度/重度缺失结构。"""
    n_days = 40
    days = np.arange(1, n_days + 1)

    mild_gap = set(range(11, 13)) | set(range(28, 31))
    mild_obs = set(days) - mild_gap

    mod_gap = set(range(9, 24)) | set(range(31, 33)) | set(range(36, 39))
    mod_obs = set(days) - mod_gap

    sev_gap = set(days)
    sev_obs: set[int] = set()

    scenarios = [
        ("轻度", mild_obs, "impute"),
        ("中度", mod_obs, "impute"),
        ("重度", sev_obs, "remove"),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(10.5, 5.6), sharex=True)
    fig.subplots_adjust(left=0.07, right=0.93, top=0.82, bottom=0.14, hspace=0.48)

    obs_color = "#4A7FB5"
    impute_face, impute_edge = "#EEF3F8", "#8EAEC9"
    remove_face, remove_edge = "#F0F1F4", "#8B95A5"
    bar_sep = "#FFFFFF"
    spine_color = "#D0D7E2"

    for ax, (tier, obs_set, gap_kind) in zip(axes, scenarios):
        ax.set_title(f"{tier}缺失", loc="left", fontsize=10, pad=10)

        for d in days:
            if d in obs_set:
                ax.bar(
                    d, 1, width=0.88, facecolor=obs_color,
                    edgecolor=bar_sep, linewidth=0.35,
                )
            elif gap_kind == "remove":
                ax.bar(
                    d, 1, width=0.88, facecolor=remove_face,
                    edgecolor=remove_edge, linewidth=0.55, hatch="xx",
                )
            else:
                ax.bar(
                    d, 1, width=0.88, facecolor=impute_face,
                    edgecolor=impute_edge, linewidth=0.55, hatch="//",
                )

        ax.set_xlim(0.5, n_days + 0.5)
        ax.set_xticks([1, 10, 20, 30, 40])
        ax.set_yticks([])
        ax.set_ylim(0, 1.12)
        ax.set_facecolor("#FAFBFC")
        for spine in ax.spines.values():
            spine.set_linewidth(0.8)
            spine.set_color(spine_color)

    obs_patch = plt.Rectangle((0, 0), 1, 1, fc=obs_color, ec=bar_sep, lw=0.5)
    impute_patch = plt.Rectangle(
        (0, 0), 1, 1, fc=impute_face, ec=impute_edge, hatch="//", lw=0.8,
    )
    remove_patch = plt.Rectangle(
        (0, 0), 1, 1, fc=remove_face, ec=remove_edge, hatch="xx", lw=0.8,
    )
    fig.legend(
        [obs_patch, impute_patch, remove_patch],
        ["有日志", "缺失（待补全）", "缺失（删除）"],
        loc="upper center",
        frameon=False,
        fontsize=8,
        ncol=3,
        bbox_to_anchor=(0.5, 0.98),
    )

    axes[-1].set_xlabel("日历日 $t$（40 天观测窗）")
    fig.savefig(
        output,
        dpi=200,
        facecolor="white",
        bbox_inches=None,
        pad_inches=0.12,
    )
    return fig


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot_timeline_schematic()
    plt.close(fig)
    print(f"saved: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
