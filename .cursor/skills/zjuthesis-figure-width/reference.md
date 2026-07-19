# 栏宽出图备忘（zjuthesis）

## 常量

- `TEXT_WIDTH_MM = 160`，`TEXT_WIDTH_IN ≈ 6.299`，`TEXT_WIDTH_PT ≈ 453.54`
- `savefig_text_width`：先 `savefig`，再按页宽 `scale_by(TEXT_WIDTH_PT / w)`；高度同比缩放

## 已验证的图类型手法

### 横向流程图（如 chap5-warning-gen）

- 节点列表 + 统一 `gap`；或 `gap = (x_right - x_left - sum(widths)) / (n-1)` 均分
- 决策「否」支路贴主链，少占高度
- 框高不够时优先加高/加宽框，而不是先加整图空白

### 泳道交互图（如 chap5-warning-handle）

- 表头 `head_h` 固定；首框顶边距 ≈ 末框底边距
- L 形箭头：先水平到目标中线再竖直；请求实线、返回虚线
- 增高整图时同步下移后续行，避免只抬 ① 造成 ①–② 大空洞

### 多面板定量图

- `figsize=(TEXT_WIDTH_IN, h)`；子图间距用 `subplots_adjust` / `constrained_layout` 控制
- 共享色条一根（同物理量）；底图例用 `fig_shared_legend`
- FPR 等极小数：列标题标 ×10⁻ⁿ，轴上用易读数值

### 热力图 / 标签示意

- 行侧冗余标注（如重复的 `$n=$`）可删，改在正文或短图注定义
- hatch 图例 swatch 与主图一致；勿为图例另发明案

### GBDT / 树状流程

- 框内 `FONT["note"]-1`；边标签更小一档；末端节点用 `gap_end` 防挤

## 正文插图

对齐后典型写法：

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics{figure/generated/foo.pdf}
    \caption{...}
    \label{fig:...}
\end{figure}
```

截图类（如 UI）可继续用 `width=\linewidth`，不强制栏宽出图。

## 难档提示

### 绝对坐标手绘

- 先估当前宽比 `w/453.54`；目标把数据坐标总宽收到 ≈ 栏宽对应的 inches
- 改坐标时保持相对拓扑；字号用 `FONT[...]`，勿写死过大 pt
- 出图仍走 `savefig_text_width` 做最终钉宽

### draw.io

- 源多在 `figure_codes/` 旁 XML 或脚本导出路径；先查 page/canvas 宽高
- `chap3-ensemble` 曾到 ~6×：优先修画布边界而非只缩文字
- 导出 PDF 后再量宽；正文同样去掉多余 `width=`

## 与用户沟通

- 「改吧」= 按当前建议做下一张/下一批
- 「只改图」= 不动 `content.tex` 论述与 float 结构
- 「矮一点 / 框大一点 / 均分」= 局部几何迭代，每次给 PDF 链接
- 下一批优先级以 `FIGURE_WIDTH_TODO.md` 未勾选项为准
