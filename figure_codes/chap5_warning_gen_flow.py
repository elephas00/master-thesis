"""第五章：预警生成流程（黑白印刷版）。

生成 figure/generated/chap5-warning-gen-flow.pdf。

用法（项目根目录）:
    python3 figure_codes/chap5_warning_gen_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from flowchart_style import (
    apply_flowchart_rc,
    arrow,
    decision,
    edge_label,
    process,
    routed_arrow,
    terminator,
)
from thesis_style import FONT, TEXT_WIDTH_IN, savefig_text_width

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap5-warning-gen-flow.pdf"


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 1.05))
    ax.set_xlim(-0.05, 12.0)
    ax.set_ylim(0.12, 1.62)
    ax.axis("off")

    y = 1.12
    fs = FONT["note"] - 1
    # 左右边距对称，剩余宽度均分到箭头间隙
    x_left, x_right = 0.12, 11.88

    wt = 0.84
    boxes = [
        ("term", "开始", wt, 0.44),
        ("proc", "拉取增量\nSMART 日志", 1.42, 0.60),
        ("proc", "数据\n预处理", 1.04, 0.56),
        ("proc", "特征/标签\n构造", 1.22, 0.56),
        ("proc", "模型推理", 1.10, 0.56),
        ("dec", "满足预\n警条件？", 1.52, 0.88),
        ("proc", "预警写入", 1.10, 0.56),
        ("term", "结束", wt, 0.44),
    ]
    widths = [w for _, _, w, _ in boxes]
    gap = (x_right - x_left - sum(widths)) / (len(boxes) - 1)

    centers: list[float] = []
    lefts: list[float] = []
    rights: list[float] = []
    x = x_left
    for kind, text, w, h in boxes:
        lefts.append(x)
        rights.append(x + w)
        c = x + w / 2
        centers.append(c)
        if kind == "term":
            terminator(ax, (c, y), w, h, text, fontsize=fs)
        elif kind == "dec":
            decision(ax, (c, y), w, h, text, fontsize=fs)
        else:
            process(ax, (c, y), w, h, text, fontsize=fs)
        x = c + w / 2 + gap

    for i in range(len(boxes) - 1):
        arrow(ax, (rights[i], y), (lefts[i + 1], y))
    edge_label(ax, ((rights[5] + lefts[6]) / 2, y + 0.14), "是", fontsize=fs)

    dec_c, dec_h = centers[5], boxes[5][3]
    end_c = centers[7]
    end_top = y - boxes[7][3] / 2
    bypass_y = 0.26
    routed_arrow(
        ax,
        [
            (dec_c, y - dec_h / 2),
            (dec_c, bypass_y),
            (end_c, bypass_y),
            (end_c, end_top),
        ],
    )
    edge_label(ax, (dec_c + 0.28, (y - dec_h / 2 + bypass_y) / 2), "否", fontsize=fs)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_pdf, pad_inches=0.02)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
