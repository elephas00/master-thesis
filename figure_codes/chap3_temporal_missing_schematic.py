"""第三章：日历级缺失补全/剔除示意

生成 figure/generated/chap3-temporal-missing-schematic.pdf。

三行子图分别示意轻度、中度、重度缺失下 40 日历日内的
有日志 / 待补全 / 整盘删除 三种状态（非真实盘数据）。

用法（项目根目录）:
    python figure_codes/chap3_temporal_missing_schematic.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    BAR_LW, C_EDGE, C_SPINE_MUTED, FONT,
    apply_rc, bar_key, bar_style, legend_swatch,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = FIGURE_DIR / "chap3-temporal-missing-schematic.pdf"

apply_rc()

# 全序：删除=b1 白；有日志=b2；待补全=b3
ST_REMOVE = bar_style(0)
ST_OBS = bar_style(1)
ST_IMPUTE = bar_style(2)
KEY_REMOVE = bar_key(0)
KEY_OBS = bar_key(1)
KEY_IMPUTE = bar_key(2)


def plot_timeline_schematic(output: Path = OUTPUT_PDF) -> plt.Figure:
    """示意：40 日历日内轻度/中度/重度缺失结构。"""
    n_days = 40
    days = np.arange(1, n_days + 1)

    mild_gap = set(range(11, 13)) | set(range(28, 31))
    mild_obs = set(days) - mild_gap

    mod_gap = set(range(9, 24)) | set(range(31, 33)) | set(range(36, 39))
    mod_obs = set(days) - mod_gap

    sev_obs: set[int] = set()

    scenarios = [
        ("轻度", mild_obs, "impute"),
        ("中度", mod_obs, "impute"),
        ("重度", sev_obs, "remove"),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(10.5, 3.2), sharex=True)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.86, bottom=0.16, hspace=0.32)

    spine_color = C_SPINE_MUTED

    for ax, (tier, obs_set, gap_kind) in zip(axes, scenarios):
        ax.set_title(f"{tier}缺失", loc="left", fontsize=FONT["title"], pad=3)

        for d in days:
            if d in obs_set:
                ax.bar(
                    d, 1, width=0.88,
                    facecolor=ST_OBS["color"],
                    edgecolor=C_EDGE,
                    linewidth=BAR_LW,
                    hatch=ST_OBS["hatch"],
                )
            elif gap_kind == "remove":
                ax.bar(
                    d, 1, width=0.88,
                    facecolor=ST_REMOVE["color"],
                    edgecolor=C_EDGE,
                    linewidth=BAR_LW,
                    hatch=ST_REMOVE["hatch"],
                )
            else:
                ax.bar(
                    d, 1, width=0.88,
                    facecolor=ST_IMPUTE["color"],
                    edgecolor=C_EDGE,
                    linewidth=BAR_LW,
                    hatch=ST_IMPUTE["hatch"],
                )

        ax.set_xlim(0.5, n_days + 0.5)
        ax.set_xticks([1, 10, 20, 30, 40])
        ax.set_yticks([])
        ax.set_ylim(0, 1.05)
        ax.set_facecolor("#FFFFFF")
        for spine in ax.spines.values():
            spine.set_linewidth(0.8)
            spine.set_color(spine_color)

    fig.legend(
        handles=[
            legend_swatch(KEY_OBS, "有日志"),
            legend_swatch(KEY_IMPUTE, "缺失（待补全）"),
            legend_swatch(KEY_REMOVE, "缺失（删除）"),
        ],
        loc="upper center",
        frameon=False,
        fontsize=FONT["legend"],
        ncol=3,
        bbox_to_anchor=(0.5, 1.0),
    )

    axes[-1].set_xlabel("日历日 $t$（40 天观测窗）", fontsize=FONT["label"])
    fig.savefig(
        output,
        facecolor="white",
        bbox_inches="tight",
        pad_inches=0.08,
    )
    return fig


def main():
    ensure_output_dirs()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot_timeline_schematic()
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
