---
name: zjuthesis-figure-width
description: >-
  Aligns Zhejiang University thesis (zjuthesis) figures to text-column width
  (~160 mm), regenerates PDFs via figure_codes scripts, and updates
  FIGURE_WIDTH_TODO. Use when adjusting 栏宽, figsize, savefig_text_width,
  flowchart layout, thesis figures, or figure/generated/*.pdf.
---

# zjuthesis 栏宽出图

目标：PDF **固有宽度 ≈ 正文栏宽**（研究生模板 A4、左右 2.5 cm → **160 mm / ≈453.54 pt**），正文用 `\includegraphics{...}` **不写** `width=\linewidth`（否则再缩一次字）。

## 必读

1. Tracker：`figure_codes/FIGURE_WIDTH_TODO.md`
2. 样式：`figure_codes/thesis_style.py`（`TEXT_WIDTH_*`、`FONT`、`savefig_text_width`、`fig_shared_legend`）
3. 流程图：`figure_codes/flowchart_style.py`

## 标准改法（matplotlib）

```python
from thesis_style import FONT, TEXT_WIDTH_IN, savefig_text_width

fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, height_in))
# ... 绘图 ...
savefig_text_width(fig, out_pdf, pad_inches=0.02)  # 保存后精确缩到栏宽
```

验收（理想 **0.90×–1.05×**）：

```bash
python3 -c "
from pathlib import Path
from pypdf import PdfReader
target = 453.54
for p in sorted(Path('figure/generated').glob('*.pdf')):
    w = float(PdfReader(str(p)).pages[0].mediabox.width)
    print(f'{w/target:5.2f}x  {p.name}')
"
```

完成后：TODO 对应行 `[ ]`→`[x]`，备注写 **1.00×**；给用户 **file://** PDF 链接。

## 字号与排版

| 角色 | 用法 |
|------|------|
| `FONT["title"]` 11 | 子图标题 |
| `FONT["label"]` 10 | 轴标签 |
| `FONT["tick"]` / `legend` 9 | 刻度、图例 |
| `FONT["note"]` / `annot` 8 | 注释、图注旁说明 |
| 流程框内 | 常用 `FONT["note"] - 1`（≈7 pt） |

- 多面板共享图例：`fig_shared_legend`（底部一条，勿每轴重复大图例）。
- 横向流程：间隙串联节点，保证箭头可见；左右边距对称，**剩余宽度均分到 gap**，勿一侧大留白。
- 泳道图：① 与表头间距 ≈ 末行与底边间距；不要为「增高」无故拉大 ①→② 垂直阶梯。
- 压矮：先收节点/菱形高度与支路留白，再收 `figsize` 高；框内文字勿贴边（略加宽/加高框）。

## 用户偏好（硬约束）

- **默认只改图**（脚本 + `figure/generated/*.pdf` + TODO）。不改正文论述/小节结构，除非用户明确要求。
- 正文若已栏宽出图：去掉该图的 `width=\linewidth`（属插图尺寸，不是改论述）。
- **不要**为「同页」重排正文段落或合并 float，除非用户明确要求。
- 图注只写读图必需信息；轴/图例已能表达的不要重复。
- 改完用渲染预览（如 PyMuPDF 出 PNG）检查：溢出、箭头压字、色条、图例。

## 难度策略

| 档 | 做法 |
|----|------|
| 易 | `figsize=(TEXT_WIDTH_IN, h)` + `savefig_text_width`；微调刻度/字号 |
| 中 | 多子图/流程：同步调字号、间距、共享图例；必要时略压高 |
| 难·绝对坐标 | 按比例重布坐标或缩小画布数据范围，再 `savefig_text_width`；忌只缩放导致糊字 |
| 难·draw.io | 缩画布/重排 XML 后导出；导出倍率用 `drawio_fs(role, scale=…)`；`chap3-ensemble` 先查画布是否异常过大 |

建议顺序：过宽最少的绝对坐标 → 其余绝对坐标 → draw.io（`ensemble` 最后）。

## 单图工作流

1. 读脚本与当前 PDF 宽/高比（`pypdf`）。
2. 改脚本对齐栏宽；流程/示意注意箭头间隙与框内边距。
3. `python3 figure_codes/<script>.py` 重出图。
4. 验收宽度；目视 PNG；更新 TODO；回复 PDF 链接。
5. 若用户说「矮一点 / 框大一点 / 均分箭头」：只调该图几何，不顺带改正文。

## 详细备忘

常见踩坑与已完成图类型经验见 [reference.md](reference.md)。
