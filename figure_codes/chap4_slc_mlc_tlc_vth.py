"""第四章：SLC / MLC / TLC 阈值电压状态对比

生成 figure/chap4-slc-mlc-tlc-vth.png / .pdf。

用法（项目根目录）:
    python3 figure_codes/chap4_slc_mlc_tlc_vth.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PNG = FIGURE_DIR / "chap4-slc-mlc-tlc-vth.png"
OUT_PDF = FIGURE_DIR / "chap4-slc-mlc-tlc-vth.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Songti SC", "Heiti TC", "Arial Unicode MS", "PingFang SC", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
})


def gauss(x, mu, sigma=0.2):
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(12, 10))
    x = np.linspace(0, 10, 2000)

    # SLC
    plt.subplot(3, 1, 1)
    plt.plot(x, gauss(x, 2.5), color="#0055cc", linewidth=3.5)
    plt.plot(x, gauss(x, 7.5), color="#0055cc", linewidth=3.5)
    plt.title("SLC (1bit/cell)  2个电压状态", fontsize=14, pad=12)
    plt.ylabel("概率", fontsize=13)
    plt.xlim(0, 10)
    plt.ylim(0, 1.2)
    plt.grid(False)
    plt.tick_params(axis="both", which="both", length=0)
    plt.xticks([])
    plt.yticks([])

    # MLC
    plt.subplot(3, 1, 2)
    for mu in [1.5, 3.5, 6.5, 8.5]:
        plt.plot(x, gauss(x, mu), color="#0055cc", linewidth=3.5)
    plt.title("MLC (2bit/cell)  4个电压状态", fontsize=14, pad=12)
    plt.ylabel("概率", fontsize=13)
    plt.xlim(0, 10)
    plt.ylim(0, 1.2)
    plt.grid(False)
    plt.tick_params(axis="both", which="both", length=0)
    plt.xticks([])
    plt.yticks([])

    # TLC
    plt.subplot(3, 1, 3)
    for mu in np.linspace(1, 9, 8):
        plt.plot(x, gauss(x, mu, sigma=0.17), color="#0055cc", linewidth=3.5)
    plt.title("TLC (3bit/cell)  8个电压状态", fontsize=14, pad=12)
    plt.xlabel("电压", fontsize=13)
    plt.ylabel("概率", fontsize=13)
    plt.xlim(0, 10)
    plt.ylim(0, 1.2)
    plt.grid(False)
    plt.tick_params(axis="both", which="both", length=0)
    plt.xticks([])
    plt.yticks([])

    fig.tight_layout()
    fig.savefig(OUT_PNG, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT_PDF, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"已生成: {OUT_PNG.name}, {OUT_PDF.name}")


if __name__ == "__main__":
    main()
