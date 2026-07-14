"""全球每年新产生的数据总量预测趋势图 (白底版)

生成 figure/chap3-data-growth-trend.png 与同名 .pdf。
数据来源：用户提供的图表 OCR 结果 (2015-2030)。
去除了灰色背景，保持白色底色。
调整了纵轴范围至 1200，并压缩了图片高度。

用法（项目根目录）:
    python figure_codes/chap3_data_growth_trend.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# --- 1. 路径与配置 (仿照原代码结构) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
# 定义输出文件名
OUT_PNG = FIGURE_DIR / "chap1-data-growth-trend.png"
OUT_PDF = FIGURE_DIR / "chap1-data-growth-trend.pdf"

# 全局绘图参数设置
plt.rcParams.update({
    # 优先使用系统支持中文的字体
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,  # 解决负号显示问题
    "figure.dpi": 120,            # 屏幕显示清晰度
    "savefig.dpi": 300,           # 保存文件清晰度
    "font.size": 10,
})

# --- 2. 数据准备 ---
years = [str(y) for y in range(2015, 2031)]
values = [11, 15, 20, 26, 33, 44, 58, 77, 102, 133, 175, 236, 325, 460, 670, 1003]


def plot_growth_trend(*, save_path_png: Path | None = None, save_path_pdf: Path | None = None) -> plt.Figure:
    # 调整 figsize: 宽度保持 12.8，高度压缩为 2.6 (约为原来的 2/3)
    fig, ax = plt.subplots(figsize=(12.8, 5))

    # 确保背景是纯白色（无灰底）
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # --- 3. 绘图逻辑 ---
    # 绘制面积图
    ax.fill_between(years, values, color='#B0C4DE', alpha=0.6, label='Data Volume')
    # 绘制顶部折线，让轮廓更清晰
    ax.plot(years, values, color='#4682B4', linewidth=1.5, marker='o', markersize=3)

    # --- 4. 坐标轴与刻度调整 ---
    # 强制设置 Y 轴刻度：从 0 到 1200，步长为 200
    ax.set_yticks(np.arange(0, 1201, 200))
    
    # 设置 X 轴刻度（每 2 年显示一个标签，避免拥挤，或者全部显示）
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, rotation=0, fontsize=8)
    
    # 隐藏顶部和右侧的边框（Spines），使图表更清爽
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')

    # 添加数据标签（模仿原图数字在点上方）
    for i, val in enumerate(values):
        # 稍微向上偏移一点，避免压在点上
        ax.text(i, val + 30, str(val), ha='center', va='bottom', fontsize=8, color='#333333')

    # 调整布局，防止标签被截断
    fig.tight_layout()

    # --- 5. 保存文件 ---
    if save_path_png is not None:
        save_path_png.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path_png, bbox_inches="tight")
    if save_path_pdf is not None:
        save_path_pdf.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path_pdf, bbox_inches="tight")

    return fig


def main() -> None:
    fig = plot_growth_trend(save_path_png=None, save_path_pdf=OUT_PDF)
    plt.close(fig)
    print(f"saved: {OUT_PNG}")
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()