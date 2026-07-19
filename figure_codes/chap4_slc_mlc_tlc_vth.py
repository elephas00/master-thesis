"""第四章：SLC / MLC / TLC 阈值电压状态对比

生成 figure/generated/chap4-slc-mlc-tlc-vth.pdf。

墨色概率密度 + 浅灰填充峰区 + 状态间虚线（读参考电压）+ 峰顶 Gray 编码。
样式：thesis_style（字体/墨色与定量图一致；几何仍为示意曲线）。

用法（项目根目录）:
    python3 figure_codes/chap4_slc_mlc_tlc_vth.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import C_EDGE, C_GRID, C_INK, C_ZERO, FONT, TEXT_WIDTH_IN, apply_rc, savefig_text_width

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap4-slc-mlc-tlc-vth.pdf"

apply_rc()


def gauss(x, mu, sigma=0.2):
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))


def _panel(ax, mus, codes, title, *, sigma=0.2, xlabel=False):
    x = np.linspace(0, 10, 2000)
    for mu in mus:
        y = gauss(x, mu, sigma=sigma)
        ax.fill_between(x, 0, y, color=C_GRID, alpha=0.85, zorder=1, linewidth=0)
        ax.plot(x, y, color=C_INK, lw=2.0, zorder=2)

    # 相邻状态中点虚线：示意读参考电压边界
    for i in range(len(mus) - 1):
        mid = 0.5 * (mus[i] + mus[i + 1])
        ax.axvline(mid, color=C_ZERO, ls="--", lw=1.0, zorder=3)

    # 峰顶编码
    for mu, code in zip(mus, codes):
        ax.text(
            mu, 1.05, code,
            ha="center", va="bottom", fontsize=FONT["tick"],
            color=C_INK, fontfamily="monospace", zorder=4,
        )

    ax.set_title(title, fontsize=FONT["title"], pad=4)
    ax.set_ylabel("概率密度（示意）", fontsize=FONT["note"])
    if xlabel:
        ax.set_xlabel(r"阈值电压 $V_{\mathrm{th}}$（示意）", fontsize=FONT["note"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.28)
    ax.tick_params(axis="both", which="both", length=0)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(C_EDGE)
    ax.spines["bottom"].set_color(C_EDGE)


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    # Gray 编码示意（由低 $V_{th}$ 到高）：教材常用写法
    panels = [
        {
            "mus": [2.5, 7.5],
            "codes": ["1", "0"],
            "title": "SLC（1 bit/cell，2 个电压状态）",
            "sigma": 0.22,
        },
        {
            "mus": [1.5, 3.5, 6.5, 8.5],
            "codes": ["11", "10", "00", "01"],
            "title": "MLC（2 bit/cell，4 个电压状态）",
            "sigma": 0.20,
        },
        {
            "mus": list(np.linspace(1.0, 9.0, 8)),
            "codes": ["111", "011", "001", "000", "010", "110", "100", "101"],
            "title": "TLC（3 bit/cell，8 个电压状态）",
            "sigma": 0.16,
        },
    ]

    fig, axes = plt.subplots(3, 1, figsize=(TEXT_WIDTH_IN, 4.2), sharex=True)
    for i, (ax, cfg) in enumerate(zip(axes, panels)):
        _panel(
            ax, cfg["mus"], cfg["codes"], cfg["title"],
            sigma=cfg["sigma"], xlabel=(i == 2),
        )

    fig.tight_layout(h_pad=0.85)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_path, pad_inches=0.04)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
