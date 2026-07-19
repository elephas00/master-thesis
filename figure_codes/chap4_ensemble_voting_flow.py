"""第四章：LP/MP/UP 分层建模 + 投票融合（黑白印刷版）。

生成 figure/generated/chap4-ensemble-voting-flow.pdf。

用法（项目根目录）:
    python3 figure_codes/chap4_ensemble_voting_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from flowchart_style import apply_flowchart_rc, arrow, process
from thesis_style import FONT, TEXT_WIDTH_IN, savefig_text_width

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap4-ensemble-voting-flow.pdf"


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 2.85))
    ax.set_xlim(0.1, 11.6)
    ax.set_ylim(0.35, 5.65)
    ax.axis("off")

    fs = FONT["note"] - 1
    gap = 0.55

    # 左 → 三模型 → 投票 → 标签；按间隙串联，保证箭头可见
    w0, w_m, w_v, w_o = 2.15, 1.85, 2.05, 2.15
    h0, h_m, h_v = 1.25, 0.95, 1.2

    c0 = 1.35
    cm = c0 + w0 / 2 + gap + w_m / 2
    cv = cm + w_m / 2 + gap + w_v / 2
    co = cv + w_v / 2 + gap + w_o / 2
    y_mid = 3.0
    models = [
        (cm, 4.55, "LightGBM\nUP"),
        (cm, y_mid, "LightGBM\nMP"),
        (cm, 1.45, "LightGBM\nLP"),
    ]

    process(
        ax, (c0, y_mid), w0, h0,
        "早期 PE 档位\nFBC 特征$\\mathbf{x}_i$", fontsize=fs,
    )
    for x, y, t in models:
        process(ax, (x, y), w_m, h_m, t, fontsize=fs)

    process(
        ax, (cv, y_mid), w_v, h_v,
        "多数投票\n（3 种页类型）", fontsize=fs,
    )
    process(
        ax, (co, y_mid), w_o, h_v,
        "块级标签\n强块 / 弱块", fontsize=fs,
    )

    for (_, y, _), vote_y in zip(models, (y_mid + 0.45, y_mid, y_mid - 0.45)):
        arrow(ax, (c0 + w0 / 2, y_mid), (cm - w_m / 2, y))
        arrow(ax, (cm + w_m / 2, y), (cv - w_v / 2, vote_y))
    arrow(ax, (cv + w_v / 2, y_mid), (co - w_o / 2, y_mid))

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_pdf, pad_inches=0.04)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
