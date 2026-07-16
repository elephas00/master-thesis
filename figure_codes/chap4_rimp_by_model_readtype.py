"""第四章：不同读模式 × 模型 × 页类型的写入量提升率

生成 figure/chap4-rimp-by-model-readtype.pdf。

方案 C：1×2 折线；横轴 LP → MP → UP → 集成，三条线=模型。

数据固化自正文表 tab:read-mode-best-default。

用法（项目根目录）:
    python3 figure_codes/chap4_rimp_by_model_readtype.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap4-rimp-by-model-readtype.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 10,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

MODELS = ["XGBoost", "LightGBM", "随机森林"]
COLS = ["LP", "MP", "UP", "集成"]
STYLES = {
    "XGBoost": {"color": "#111111", "ls": "-", "marker": "o"},
    "LightGBM": {"color": "#666666", "ls": "--", "marker": "s"},
    "随机森林": {"color": "#999999", "ls": "-.", "marker": "^"},
}

DATA = {
    "BestRead": {
        "LP": [-6.11, -11.76, -11.76],
        "MP": [11.43, 11.99, -0.45],
        "UP": [-11.76, -11.76, -11.76],
        "集成": [11.43, 11.99, -0.45],
    },
    "DefaultRead": {
        "LP": [17.08, 17.08, 17.08],
        "MP": [15.95, 14.82, 16.52],
        "UP": [0.68, -2.71, 17.08],
        "集成": [17.08, 17.08, 17.08],
    },
}


def _series_for_model(read_type: str, model_idx: int) -> list[float]:
    return [DATA[read_type][col][model_idx] for col in COLS]


def _draw_panel(ax, read_type: str, *, show_ylabel: bool, show_legend: bool) -> None:
    x = np.arange(len(COLS))
    for i, model in enumerate(MODELS):
        ys = _series_for_model(read_type, i)
        st = STYLES[model]
        ax.plot(
            x, ys,
            color=st["color"], ls=st["ls"], marker=st["marker"],
            lw=1.7, ms=6, label=model, zorder=3,
        )

    ax.axhline(0, color="#444444", lw=0.9, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(COLS)
    ax.set_title(read_type, fontsize=11, pad=6)
    if show_ylabel:
        ax.set_ylabel(r"$R_{\mathrm{imp}}$ / \%")
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    if show_legend:
        ax.legend(frameon=False, loc="best", fontsize=8.5)


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8), sharey=True)

    _draw_panel(axes[0], "BestRead", show_ylabel=True, show_legend=True)
    _draw_panel(axes[1], "DefaultRead", show_ylabel=False, show_legend=False)

    all_vals = [v for rt in DATA.values() for col in COLS for v in rt[col]]
    ymin, ymax = min(all_vals), max(all_vals)
    axes[0].set_ylim(ymin - 2.5, ymax + 2.5)

    fig.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
