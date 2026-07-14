"""第三章：日历缺失分布

生成 figure/temporal-missing-distribution.png。

数据固化自「清洗前」盘级时序质量：
  data/preprocess/{MB1,MB2}_selected.parquet.pre_early_drop
（字段筛选后、删除早期样本 / 故障后日志 / 短观测 / 重度缺失、日历补全之前）。
与正文表 tab:temporal-quality-summary 一致（MB1 44401 / MB2 48811）。

勿使用当前 selected.parquet / imputed.parquet：二者已剔除重度缺失盘，
图中重度档会近乎为 0。

用法（项目根目录）:
    python3 figure_codes/chap3_temporal_missing_distribution.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUTPUT_PNG = FIGURE_DIR / "temporal-missing-distribution.png"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
})

MAX_GAP_LABELS = ["0", "1–7", "8–30", "31–90", ">90"]
COV_LABELS = ["<0.5", "0.5–0.8", "0.8–0.95", "≥0.95"]
RULE_LABELS = ["轻度\n(拟进入补全)", "中度\n(拟进入补全)", "重度\n(拟整盘剔除)"]
COLORS = {"MB1": "#2563EB", "MB2": "#F97316"}

# 各型号磁盘数与分档计数（占比在绘图时换算）
# 源：data/preprocess/{MB1,MB2}_selected.parquet.pre_early_drop
# 算法与 codes/eda/scripts/stat_disk_temporal_quality.py 一致（补全/剔盘之前）。
N_DISKS = {"MB1": 44401, "MB2": 48811}
GAP_COUNTS = {
    # G_max：0, 1–7, 8–30, 31–90, >90
    "MB1": [252, 28933, 9086, 2494, 3636],
    "MB2": [246, 30733, 10043, 2607, 5182],
}
COV_COUNTS = {
    # cov：<0.5, 0.5–0.8, 0.8–0.95, ≥0.95
    "MB1": [337, 3355, 10458, 30251],
    "MB2": [1422, 4857, 8593, 33939],
}
# 轻度 max_gap<=7；中度 8..30；重度 max_gap>30 或 cov<0.5（占比 / %）
RULE_PCT = {
    "MB1": [65.73, 20.46, 13.81],
    "MB2": [63.47, 20.58, 15.96],
}


def _pct(counts: list[int]) -> np.ndarray:
    arr = np.asarray(counts, dtype=float)
    return 100.0 * arr / arr.sum()


def plot(*, save_path: Path = OUTPUT_PNG) -> plt.Figure:
    models = ["MB1", "MB2"]
    width = 0.36
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))

    ax = axes[0]
    x = np.arange(len(MAX_GAP_LABELS))
    for i, model in enumerate(models):
        ax.bar(
            x + (i - 0.5) * width,
            _pct(GAP_COUNTS[model]),
            width=width,
            label=model,
            color=COLORS[model],
            alpha=0.92,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(MAX_GAP_LABELS)
    ax.set_xlabel(r"最长连续缺失天数 $G_{\max}$")
    ax.set_ylabel(r"磁盘占比 / \%")
    ax.set_title("(a) 按最长中断分档")
    ax.legend(frameon=False)
    ax.set_ylim(0, max(75, ax.get_ylim()[1] * 1.05))
    ax.grid(axis="y", alpha=0.25, linestyle="--")

    ax = axes[1]
    x = np.arange(len(COV_LABELS))
    for i, model in enumerate(models):
        ax.bar(
            x + (i - 0.5) * width,
            _pct(COV_COUNTS[model]),
            width=width,
            label=model,
            color=COLORS[model],
            alpha=0.92,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(COV_LABELS)
    ax.set_xlabel(r"日历覆盖率 $\mathrm{cov}=n_{\mathrm{obs}}/\mathrm{span}$")
    ax.set_ylabel(r"磁盘占比 / \%")
    ax.set_title("(b) 按覆盖率分档")
    ax.grid(axis="y", alpha=0.25, linestyle="--")

    ax = axes[2]
    for j, model in enumerate(models):
        xs = np.arange(3) + (j - 0.5) * width
        ax.bar(xs, RULE_PCT[model], width=width, label=model, color=COLORS[model], alpha=0.92)
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(RULE_LABELS)
    ax.set_ylabel(r"磁盘占比 / \%")
    ax.set_title("(c) 预处理分流（示意阈值）")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.25, linestyle="--")

    fig.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=180, bbox_inches="tight")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
