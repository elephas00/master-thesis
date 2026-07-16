"""$W$–$k$ 网格搜索热力图（方案 A2）

生成 figure/chap3-wk-grid-heatmap-A.pdf。

对应 notebook `codes/eda/notebooks/eda_wk_grid_heatmap.ipynb` §A2：
- `cmap=CMAP_HEAT`（饱和蓝阶，与 thesis_style 一致）
- 色标聚焦 $W{\\geq}1$（MB2 另排除 $k{=}0$ 列），$W{=}0$ 行浅灰底
- 最优格 $(W^\\ast, k^\\ast)$ 加粗框 + ★

数据固化自正文表 `tab:chap3-wk-grid`。

用法（项目根目录）:
    python figure_codes/chap3_wk_grid_heatmap.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from thesis_style import CMAP_HEAT, apply_rc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap3-wk-grid-heatmap-A.pdf"

apply_rc()
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": 10,
})

MODELS = ["MB1", "MB2"]
CMAP_ABS = CMAP_HEAT

# 行=W，列=k；来源 content.tex tab:chap3-wk-grid
F05 = {
    "MB1": np.array([
        [0.000, 0.362, 0.077, 0.602, 0.865],
        [0.800, 0.918, 0.919, 0.921, 0.915],
        [0.865, 0.902, 0.901, 0.900, 0.904],
        [0.849, 0.881, 0.877, 0.872, 0.881],
    ], dtype=float),
    "MB2": np.array([
        [0.359, 0.478, 0.478, 0.478],
        [0.249, 0.478, 0.467, 0.458],
        [0.296, 0.478, 0.490, 0.478],
        [0.249, 0.478, 0.474, 0.478],
    ], dtype=float),
}

K_LABELS = {"MB1": list(range(5)), "MB2": list(range(4))}
OPTIMAL = {"MB1": (1, 3), "MB2": (2, 2)}
VMIN_VMAX = {"MB1": (0.0, 1.0), "MB2": (0.20, 0.50)}


def _text_color(val: float, vmin: float, vmax: float, *, force_dark: bool = False) -> str:
    if force_dark:
        return "#0F172A"
    if vmax <= vmin:
        return "#0F172A"
    t = (val - vmin) / (vmax - vmin)
    return "white" if t > 0.48 else "#0F172A"


def compute_zoom_limits(
    mat: np.ndarray, *, row_start: int = 1, col_start: int = 0, margin: float = 0.08,
) -> tuple[float, float]:
    sub = mat[row_start:, col_start:]
    vmin, vmax = float(sub.min()), float(sub.max())
    span = max(vmax - vmin, 1e-9)
    return vmin - margin * span, vmax + margin * span


def _annotate_cells(
    ax,
    mat: np.ndarray,
    *,
    optimal: tuple[int, int],
    vmin: float,
    vmax: float,
    fmt: str = "{:.3f}",
    mark_optimal: bool = True,
    mute_row0: bool = False,
) -> None:
    ow, ok = optimal
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat[i, j]
            is_opt = (i, j) == (ow, ok)
            label = fmt.format(val)
            if is_opt and mark_optimal:
                label += "\n★"
            ax.text(
                j, i, label,
                ha="center", va="center", fontsize=8,
                color=_text_color(val, vmin, vmax, force_dark=(mute_row0 and i == 0)),
                fontweight="bold" if is_opt else "normal",
                zorder=6,
            )
    if mark_optimal:
        ax.add_patch(Rectangle(
            (ok - 0.5, ow - 0.5), 1, 1,
            fill=False, edgecolor="#111827", linewidth=2.4, zorder=5,
        ))


def _mute_row0(ax, n_cols: int) -> None:
    ax.add_patch(Rectangle(
        (-0.5, -0.5), n_cols, 1,
        facecolor="#E5E7EB", edgecolor="#9CA3AF", linewidth=0.8, zorder=2, alpha=0.72,
    ))


def _style_wk_axes(ax, mat: np.ndarray, k_labels: list[int], *, title: str) -> None:
    ax.set_xticks(range(len(k_labels)))
    ax.set_xticklabels([f"$k={k}$" for k in k_labels])
    ax.set_yticks(range(mat.shape[0]))
    ax.set_yticklabels([f"$W={w}$" for w in range(mat.shape[0])])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title, fontweight="bold", pad=8)


def plot_wk_panel(
    ax,
    mat: np.ndarray,
    model: str,
    *,
    cmap: str = CMAP_ABS,
    vmin: float | None = None,
    vmax: float | None = None,
    mark_optimal: bool = True,
    zoom_row_start: int | None = None,
    zoom_col_start: int = 0,
    mute_row0: bool = False,
):
    k_labels = K_LABELS[model]
    if vmin is None or vmax is None:
        if zoom_row_start is not None:
            zmin, zmax = compute_zoom_limits(
                mat, row_start=zoom_row_start, col_start=zoom_col_start,
            )
            vmin = zmin if vmin is None else vmin
            vmax = zmax if vmax is None else vmax
        else:
            vmin = VMIN_VMAX[model][0] if vmin is None else vmin
            vmax = VMIN_VMAX[model][1] if vmax is None else vmax

    im = ax.imshow(mat, aspect="equal", cmap=cmap, vmin=vmin, vmax=vmax, origin="upper")
    if mute_row0:
        _mute_row0(ax, mat.shape[1])
    _style_wk_axes(ax, mat, k_labels, title=model)
    _annotate_cells(
        ax, mat, optimal=OPTIMAL[model], vmin=vmin, vmax=vmax,
        mark_optimal=mark_optimal, mute_row0=mute_row0,
    )
    return im, (vmin, vmax)


def plot_heatmap(*, save_path_pdf: Path | None = None) -> plt.Figure:
    # 按相同方格边长定位；两图紧挨并排（正常子图间距）
    cell = 0.56
    n_rows = 4
    n_cols = [len(K_LABELS[m]) for m in MODELS]
    y_label = 0.46
    cbar_w, cbar_pad = 0.16, 0.04
    panel_gap = 0.42  # 左色条刻度文字 → 右 y 标签
    left_m, right_m, bot_m, top_m = 0.02, 0.02, 0.40, 0.42

    panel_w = [y_label + n * cell + cbar_pad + cbar_w for n in n_cols]
    fig_w = left_m + panel_w[0] + panel_gap + panel_w[1] + right_m
    fig_h = bot_m + n_rows * cell + top_m
    fig = plt.figure(figsize=(fig_w, fig_h))

    def _panel_axes(x0: float, n_col: int):
        ax = fig.add_axes([
            (x0 + y_label) / fig_w,
            bot_m / fig_h,
            (n_col * cell) / fig_w,
            (n_rows * cell) / fig_h,
        ])
        cax = fig.add_axes([
            (x0 + y_label + n_col * cell + cbar_pad) / fig_w,
            bot_m / fig_h,
            cbar_w / fig_w,
            (n_rows * cell) / fig_h,
        ])
        return ax, cax

    xs = [left_m, left_m + panel_w[0] + panel_gap]
    for x0, model, nc in zip(xs, MODELS, n_cols):
        ax, cax = _panel_axes(x0, nc)
        col_start = 1 if model == "MB2" else 0
        im, _ = plot_wk_panel(
            ax, F05[model], model,
            zoom_row_start=1,
            zoom_col_start=col_start,
            mute_row0=True,
        )
        cbar = fig.colorbar(im, cax=cax)
        cbar.ax.set_title(r"$F_{0.5}$", fontsize=9, pad=3)
        cbar.ax.tick_params(labelsize=7, pad=1)

    if save_path_pdf is not None:
        fig.savefig(save_path_pdf, bbox_inches="tight", pad_inches=0.02)

    return fig


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot_heatmap(save_path_pdf=OUT_PDF)
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
