"""第三章：B 组属性故障前时序示意（MB1 / MB2）

使用 figure_codes/chap3_b_group_mutation_eda_data.json 中的冻结观测，
生成：
    figure/chap3-b-group-mutation-eda-mb1.pdf
    figure/chap3-b-group-mutation-eda-mb2.pdf

数据快照来源：codes/eda/scripts/plot_b_group_mutation_combined.py
（MB1 2019-06 六块盘；MB2 2018-11 六块盘；仅 is_imputed=False 原始观测日）。

用法（项目根目录）:
    python figure_codes/chap3_b_group_mutation_eda.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
DATA_PATH = HERE / "chap3_b_group_mutation_eda_data.json"
FIGURE_DIR = PROJECT_ROOT / "figure"

ATTR_LABEL = {
    "r_5": "重映射扇区计数",
    "r_180": "未用的备用块计数",
    "r_183": "串口降速错误计数",
    "n_180": "未用的备用块计数(归一化)",
    "r_199": "Ultra ATA CRC 错误率",
}

OUTPUTS = {
    "MB1": FIGURE_DIR / "chap3-b-group-mutation-eda-mb1.pdf",
    "MB2": FIGURE_DIR / "chap3-b-group-mutation-eda-mb2.pdf",
}

COLORS = plt.cm.tab10.colors


def _parse_day(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


def plot_model(model: str, bundle: dict) -> Path:
    plot_start = _parse_day(bundle["plot_start"])
    plot_end = _parse_day(bundle["plot_end"])
    date_label = (
        f"{plot_start.strftime('%Y-%m')} ~ {plot_end.strftime('%Y-%m')}"
    )
    cols = bundle["cols"]
    disk_ids = bundle["disk_ids"]
    series = bundle["series"]

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0))
    legend_handles: list = []
    legend_labels: list[str] = []

    for col_idx, col in enumerate(cols):
        ax = axes[col_idx]
        for i, disk_id in enumerate(disk_ids):
            points = series.get(disk_id, [])
            if not points:
                continue

            ds = [_parse_day(p["ds"]) for p in points]
            ys = [p[col] for p in points]
            ft = _parse_day(points[0]["failure_time"])
            ft_str = ft.strftime("%m-%d")
            color = COLORS[i % len(COLORS)]

            (line,) = ax.plot(
                ds,
                ys,
                marker="o",
                ms=3,
                lw=1.3,
                alpha=0.85,
                color=color,
            )
            ax.axvline(ft, color="crimson", ls="--", lw=0.9, alpha=0.45)
            if col_idx == 0:
                legend_handles.append(line)
                legend_labels.append(f"disk {disk_id} (fail {ft_str})")

        ax.set_xlim(plot_start, plot_end)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        ax.set_ylabel("读数", fontsize=9)
        panel = chr(ord("a") + col_idx)
        ax.set_title(f"({panel}) {col} {ATTR_LABEL[col]}", fontsize=10, pad=6)
        ax.grid(True, alpha=0.25)
        ax.set_xlabel(f"日期（{date_label}）", fontsize=9)

    fig.legend(
        legend_handles,
        legend_labels,
        loc="lower center",
        ncol=3,
        fontsize=8,
        bbox_to_anchor=(0.5, -0.14),
        frameon=True,
    )
    fig.autofmt_xdate(rotation=0, ha="center")
    fig.tight_layout()

    output = OUTPUTS[model]
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output


def main() -> None:
    plt.rcParams.update(
        {
            "font.sans-serif": [
                "Arial Unicode MS",
                "SimHei",
                "PingFang SC",
                "DejaVu Sans",
            ],
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for model in ("MB1", "MB2"):
        path = plot_model(model, data[model])
        print(f"已保存 {path}")


if __name__ == "__main__":
    main()
