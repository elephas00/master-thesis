"""第三章：B 组属性故障前时序示意（MB1 / MB2）

使用 figure_codes/chap3_b_group_mutation_eda_data.json 中的冻结观测，
生成：
    figure/generated/chap3-b-group-mutation-eda-mb1.pdf
    figure/generated/chap3-b-group-mutation-eda-mb2.pdf

数据快照来源：codes/eda/scripts/plot_b_group_mutation_combined.py
（MB1 2019-06 六块盘；MB2 2018-11 六块盘；展示窗约 1.5 个月；
仅 is_imputed=False 原始观测日）。

用法（项目根目录）:
    python figure_codes/chap3_b_group_mutation_eda.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    FONT,
    TEXT_WIDTH_IN,
    apply_rc,
    fig_shared_legend,
    line_style,
    savefig_text_width,
)

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
DATA_PATH = HERE / "chap3_b_group_mutation_eda_data.json"

ATTR_LABEL = {
    "r_5": "重映射扇区计数",
    "r_180": "未用的备用块计数",
    "r_183": "串口降速错误计数",
    "n_180": "未用的备用块计数",
    "r_199": "Ultra ATA CRC 错误率",
}

OUTPUTS = {
    "MB1": FIGURE_DIR / "chap3-b-group-mutation-eda-mb1.pdf",
    "MB2": FIGURE_DIR / "chap3-b-group-mutation-eda-mb2.pdf",
}

apply_rc()


def _parse_day(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def plot_model(model: str, bundle: dict) -> Path:
    plot_start = _parse_day(bundle["plot_start"])
    plot_end = _parse_day(bundle["plot_end"])
    cols = bundle["cols"]
    disk_ids = bundle["disk_ids"]
    series = bundle["series"]

    # 按版心宽度出图，避免正文 width= 缩放缩字号
    fig, axes = plt.subplots(1, 3, figsize=(TEXT_WIDTH_IN, 2.25))
    legend_handles: list = []
    legend_labels: list[str] = []

    for col_idx, col in enumerate(cols):
        ax = axes[col_idx]
        for i, disk_id in enumerate(disk_ids):
            points = [
                p
                for p in series.get(disk_id, [])
                if plot_start <= _parse_day(p["ds"]) <= plot_end
            ]
            if not points:
                continue

            ds = [_parse_day(p["ds"]) for p in points]
            ys = [p[col] for p in points]
            ft = _parse_day(points[0]["failure_time"])
            ft_str = ft.strftime("%m-%d")
            st = line_style(i)

            (line,) = ax.plot(
                ds,
                ys,
                marker=st["marker"],
                ms=3.5,
                lw=1.3,
                ls=st["ls"],
                alpha=0.95,
                color=st["color"],
            )
            ax.axvline(ft, color="#444444", ls="--", lw=0.8, alpha=0.55)
            if col_idx == 0:
                legend_handles.append(line)
                legend_labels.append(f"disk {disk_id} (fail {ft_str})")

        ax.set_xlim(plot_start, plot_end)
        # 约 1.5 个月窗内 MonthLocator 往往只落 1 个刻度；显式标出起止日
        month_start = plot_end.replace(day=1)
        xticks = [plot_start]
        if plot_start < month_start < plot_end:
            xticks.append(month_start)
        xticks.append(plot_end)
        ax.set_xticks(xticks)
        # 栏宽下三列较窄：用月-日，避免 YYYY-MM-DD 挤叠
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        ax.tick_params(axis="both", labelsize=FONT["tick"])
        panel = chr(ord("a") + col_idx)
        ax.set_title(f"({panel}) {col} {ATTR_LABEL[col]}", fontsize=FONT["title"], pad=4)
        ax.grid(True, alpha=0.25)

    fig.subplots_adjust(left=0.07, right=0.99, top=0.86, bottom=0.30, wspace=0.30)
    fig_shared_legend(
        fig,
        legend_handles,
        legend_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.02),
        ncol=3,
        handlelength=2.4,
        handletextpad=0.45,
        columnspacing=0.9,
        fontsize=FONT["note"],
    )

    output = OUTPUTS[model]
    output.parent.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, output, pad_inches=0.02)
    plt.close(fig)
    return output


def main() -> None:
    ensure_output_dirs()
    apply_rc()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for model in ("MB1", "MB2"):
        path = plot_model(model, data[model])
        print(f"已保存 {path}")


if __name__ == "__main__":
    main()
