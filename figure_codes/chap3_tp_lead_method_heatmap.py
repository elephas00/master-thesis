"""多方法 TP 提前预警天数热力图（方案 E）

生成 figure/generated/chap3-tp-lead-method-E-heatmap.pdf。

列：$d=0..7$ 逐日 + $d=8$–$30$ 合并；格内为 TP 盘数，底色为占该方法合计 TP 的比例。
数据已固化，来源 eda/run/tp_lead_time_test_*_summary.json（2026-07-10）。

用法（项目根目录）:
    python figure_codes/chap3_tp_lead_method_heatmap.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import CMAP_HEAT, apply_rc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap3-tp-lead-method-E-heatmap.pdf"

apply_rc()
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": 10,
})

MODELS = ["MB1", "MB2"]
METHODS = ["本文方法", "RF", "AE", "MVT-RF", "Mut-RF"]
D_MAX = 7
TAIL_HI = 30
COL_LABELS = [str(k) for k in range(D_MAX + 1)] + [f"{D_MAX + 1}–{TAIL_HI}"]

# 各型号 × 方法 × [d=0..7, d=8–30] 的 TP 盘数
BUCKET_COUNTS: dict[str, dict[str, list[int]]] = {
    "MB1": {
        "本文方法": [20, 127, 0, 0, 0, 0, 1, 0, 1],
        "RF": [5, 148, 0, 0, 0, 0, 1, 0, 3],
        "AE": [1, 3, 0, 0, 0, 0, 0, 0, 3],
        "MVT-RF": [5, 149, 0, 0, 0, 0, 1, 0, 1],
        "Mut-RF": [0, 0, 0, 0, 0, 0, 0, 0, 4],
    },
    "MB2": {
        "本文方法": [7, 1, 0, 0, 0, 1, 0, 0, 1],
        "RF": [4, 1, 0, 0, 0, 0, 0, 0, 0],
        "AE": [5, 1, 0, 0, 0, 0, 0, 0, 0],
        "MVT-RF": [7, 1, 0, 0, 0, 0, 0, 0, 0],
        "Mut-RF": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
}


def _counts_to_share(counts: list[int]) -> np.ndarray:
    total = sum(counts)
    if total <= 0:
        return np.zeros(len(counts), dtype=float)
    return np.asarray(counts, dtype=float) / total


def plot_heatmap(*, save_path_pdf: Path | None = None) -> plt.Figure:
    # 缩小方格物理尺寸，字号保持不变
    cell = 0.42
    n_rows = len(METHODS)
    n_cols = len(COL_LABELS)
    y_label = 1.55
    cbar_w, cbar_pad = 0.18, 0.06
    panel_gap = 0.55
    left_m, right_m, bot_m, top_m = 0.05, 0.05, 0.55, 0.42

    panel_w = y_label + n_cols * cell + cbar_pad + cbar_w
    fig_w = left_m + 2 * panel_w + panel_gap + right_m
    fig_h = bot_m + n_rows * cell + top_m
    fig = plt.figure(figsize=(fig_w, fig_h))

    def _panel_axes(x0: float):
        ax = fig.add_axes([
            (x0 + y_label) / fig_w,
            bot_m / fig_h,
            (n_cols * cell) / fig_w,
            (n_rows * cell) / fig_h,
        ])
        cax = fig.add_axes([
            (x0 + y_label + n_cols * cell + cbar_pad) / fig_w,
            bot_m / fig_h,
            cbar_w / fig_w,
            (n_rows * cell) / fig_h,
        ])
        return ax, cax

    xs = [left_m, left_m + panel_w + panel_gap]
    for x0, model in zip(xs, MODELS):
        ax, cax = _panel_axes(x0)
        count_rows = [BUCKET_COUNTS[model][method] for method in METHODS]
        share_rows = [_counts_to_share(row) for row in count_rows]
        mat_count = np.asarray(count_rows, dtype=int)
        mat_share = np.asarray(share_rows, dtype=float)

        vmax = mat_share.max() if mat_share.size else 1.0
        im = ax.imshow(
            mat_share, aspect="equal", cmap=CMAP_HEAT, vmin=0, vmax=max(vmax, 0.05),
        )

        row_labels = [
            f"{method}  ($n$={int(mat_count[i].sum())})"
            for i, method in enumerate(METHODS)
        ]
        ax.set_yticks(range(len(METHODS)))
        ax.set_yticklabels(row_labels, fontsize=8)
        ax.set_xticks(range(len(COL_LABELS)))
        ax.set_xticklabels(COL_LABELS, fontsize=8)
        ax.set_xlabel("提前天数 $d$（天）", fontsize=10)
        ax.set_title(model, fontweight="bold", fontsize=10, pad=6)

        for i in range(len(METHODS)):
            for j in range(len(COL_LABELS)):
                cnt = int(mat_count[i, j])
                share = float(mat_share[i, j])
                if cnt <= 0:
                    continue
                ax.text(
                    j,
                    i,
                    str(cnt),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if share > 0.48 else "#0F172A",
                )

        cbar = fig.colorbar(im, cax=cax)
        cbar.set_label("TP 占比", fontsize=9)
        cbar.ax.tick_params(labelsize=7, pad=1)

    if save_path_pdf is not None:
        fig.savefig(save_path_pdf, bbox_inches="tight", pad_inches=0.02)

    return fig


def main() -> None:
    ensure_output_dirs()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot_heatmap(save_path_pdf=OUT_PDF)
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
