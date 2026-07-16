"""第四章：SLC / MLC / TLC 阈值电压状态对比

生成 figure/chap4-slc-mlc-tlc-vth.pdf。

黑白曲线 + 状态间虚线（示意读参考电压）+ 峰顶 Gray 编码。

用法（项目根目录）:
    python3 figure_codes/chap4_slc_mlc_tlc_vth.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap4-slc-mlc-tlc-vth.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "Songti SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

C_CURVE = "#111111"
C_DASH = "#555555"
C_TEXT = "#111111"


def gauss(x, mu, sigma=0.2):
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))


def _panel(ax, mus, codes, title, *, sigma=0.2, xlabel=False):
    x = np.linspace(0, 10, 2000)
    for mu in mus:
        ax.plot(x, gauss(x, mu, sigma=sigma), color=C_CURVE, lw=2.2)

    # 相邻状态中点虚线：示意读参考电压边界
    for i in range(len(mus) - 1):
        mid = 0.5 * (mus[i] + mus[i + 1])
        ax.axvline(mid, color=C_DASH, ls="--", lw=1.0, zorder=1)

    # 峰顶编码
    for mu, code in zip(mus, codes):
        ax.text(
            mu, 1.05, code,
            ha="center", va="bottom", fontsize=10,
            color=C_TEXT, fontfamily="monospace", zorder=3,
        )

    ax.set_title(title, fontsize=12, pad=8)
    ax.set_ylabel("概率密度（示意）", fontsize=10)
    if xlabel:
        ax.set_xlabel(r"阈值电压 $V_{\mathrm{th}}$（示意）", fontsize=10)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.28)
    ax.tick_params(axis="both", which="both", length=0)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


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

    fig, axes = plt.subplots(3, 1, figsize=(9.5, 7.2), sharex=True)
    for i, (ax, cfg) in enumerate(zip(axes, panels)):
        _panel(
            ax, cfg["mus"], cfg["codes"], cfg["title"],
            sigma=cfg["sigma"], xlabel=(i == 2),
        )

    fig.tight_layout(h_pad=1.2)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
