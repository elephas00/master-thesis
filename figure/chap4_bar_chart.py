import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据：6个块的PE次数
# 注意：您提到有6个数据，但只列出了5个值，这里假设第6个也是10000
# 如果需要修改，请调整下面的pe_values列表
pe_values = [8000, 8500, 9500, 10000, 10000, 10000]  # 6个数据值

# 创建图形
fig, ax = plt.subplots(figsize=(5, 3))

# 块的标签（从上到下）
block_labels = [f'块{i+1}' for i in range(len(pe_values))]

# 阈值
threshold = 8000

# 计算左侧（灰色）和右侧（绿色）的长度
left_values = [min(pe, threshold) for pe in pe_values]  # 左侧灰色部分
right_values = [max(0, pe - threshold) for pe in pe_values]  # 右侧绿色部分

# 绘制左侧灰色部分（从0开始）
bars_left = ax.barh(range(len(pe_values)), left_values, 
                    color='gray', edgecolor='black', linewidth=1)

# 绘制右侧绿色部分（从threshold开始，使用left参数指定起始位置）
bars_right = ax.barh(range(len(pe_values)), right_values, 
                     left=left_values, color='green', edgecolor='black', linewidth=1)

# 在x=8000处添加垂直虚线
ax.axvline(x=threshold, color='black', linestyle='--', linewidth=1.5, label='固定阈值策略每个块的PE')

# 设置y轴标签
ax.set_yticks(range(len(pe_values)))
ax.set_yticklabels(block_labels)

# 设置x轴标签
ax.set_xlabel('每个块理想PE次数', fontsize=12)

# 移除y轴标签（无纵坐标）
ax.set_ylabel('')

# 设置x轴范围，留出一些边距
ax.set_xlim(0, max(pe_values) * 1.1)

# 添加图例
# 创建自定义图例元素
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='gray', edgecolor='black'),
    Patch(facecolor='green', edgecolor='black'),
]
ax.legend(handles=legend_elements, labels=['固定阈值策略每个块的PE次数', '理想策略可额外使用的PE次数'], 
          loc='best', fontsize=10)

# 在柱状图上添加数值标签（显示在右侧）
for i, pe in enumerate(pe_values):
    ax.text(pe, i, f'{pe}', ha='left', va='center', fontsize=10, 
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

# 调整布局
plt.tight_layout()

# 保存图片
plt.savefig('chap4_pe_comparison.pdf', dpi=300, bbox_inches='tight')
plt.savefig('chap4_pe_comparison.png', dpi=300, bbox_inches='tight')

# 显示图片
plt.show()

print("图表已保存为 figure/chap4_pe_comparison.pdf 和 figure/chap4_pe_comparison.png")

