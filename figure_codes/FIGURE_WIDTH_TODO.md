# 图片栏宽对齐待办

目标：出图 PDF 固有宽度接近正文栏宽（研究生模板 A4、左右边距 2.5 cm → **约 160 mm / 453 pt**），正文使用 `\includegraphics{...}` 默认尺寸插入、不再依赖 `width=` 强制缩放。

更新：2026-07-19（保留：数据增长 / W–k 热力图 / PE 对比；其余易档已回滚）

公共工具：`thesis_style.TEXT_WIDTH_*` + `savefig_text_width()`（保存后精确缩放到 160 mm）。

## 难易度说明

| 等级 | 含义 |
|------|------|
| 易 | 改 `figsize` / 微调即可，或已接近栏宽 |
| 中 | 多子图或流程，需同步调字号/间距/排版 |
| 难 | 绝对坐标手绘，或 draw.io XML 整页重排；画布显著过大 |

## 待办一览

| 状态 | 难易 | 图片 | 代码 | 现宽/栏宽 | 备注 |
|------|------|------|------|-----------|------|
| [x] | 易 | `figure/generated/chap1-data-growth-trend.pdf` | `figure_codes/chap1_data_grow_trend.py` | **1.00×** | 已对齐（保留） |
| [ ] | 易 | `figure/generated/chap2-gbdt.pdf` | `figure_codes/chap2_gbdt_graph.py` | ~1.20× | 已回滚 |
| [ ] | 易 | `figure/generated/chap3-failure-by-month.pdf` | `figure_codes/chap3_failure_by_month.py` | ~1.58× | 已回滚 |
| [x] | 易 | `figure/generated/chap3-wk-grid-heatmap-A.pdf` | `figure_codes/chap3_wk_grid_heatmap.py` | **1.00×** | 已对齐（保留） |
| [x] | 易 | `figure/generated/chap4-program-erase-comparison.pdf` | `figure_codes/chap4_program_erase_comparision.py` | **1.00×** | 已对齐（保留） |
| [ ] | 易 | `figure/generated/chap4-block-labeling-flow.pdf` | `figure_codes/chap4_block_labeling_flow.py` | ~1.08× | 已回滚 |
| [ ] | 易 | `figure/generated/chap4-ensemble-voting-flow.pdf` | `figure_codes/chap4_ensemble_voting_flow.py` | ~0.95× | 已回滚 |
| [ ] | 易 | `figure/chap5-ui-warning.png` | （无脚本，截图） | — | 导出时按栏宽裁/缩 |
| [ ] | 中 | `figure/generated/chap3-temporal-missing-schematic.pdf` | `figure_codes/chap3_temporal_missing_schematic.py` | ~1.56× | 改宽 + 字号 |
| [ ] | 中 | `figure/generated/chap3-temporal-missing-distribution.pdf` | `figure_codes/chap3_temporal_missing_distribution.py` | ~1.97× | 1×3，需压缩/改排 |
| [ ] | 中 | `figure/generated/chap3-b-group-mutation-eda-mb1.pdf` | `figure_codes/chap3_b_group_mutation_eda.py` | ~2.13× | 同脚本出 MB1/MB2 |
| [ ] | 中 | `figure/generated/chap3-b-group-mutation-eda-mb2.pdf` | `figure_codes/chap3_b_group_mutation_eda.py` | ~2.13× | 同上 |
| [x] | 中 | `figure/generated/chap3-first-jump-pmf.pdf` | `figure_codes/chap3_first_jump_pmf.py` | **1.00×** | 已对齐（无跳变靠左+折线+inset） |
| [ ] | 中 | `figure/generated/chap3-label-strategy.pdf` | `figure_codes/chap3_label_strategy.py` | ~1.72× | 多列示意 |
| [ ] | 中 | `figure/generated/chap3-tp-lead-method-E-heatmap.pdf` | `figure_codes/chap3_tp_lead_method_heatmap.py` | ~1.85× | 双面板热力 |
| [x] | 中 | `figure/generated/chap3-tp-lead-time-test.pdf` | `figure_codes/chap3_tp_lead_time_test.py` | **1.00×** | 已对齐（近端分面+远端时间轴） |
| [ ] | 中 | `figure/generated/chap4-slc-mlc-tlc-vth.pdf` | `figure_codes/chap4_slc_mlc_tlc_vth.py` | ~1.49× | 3 行曲线 |
| [ ] | 中 | `figure/generated/chap4-rimp-by-model-readtype.pdf` | `figure_codes/chap4_rimp_by_model_readtype.py` | ~1.65× | 1×2 |
| [ ] | 中 | `figure/generated/chap4-lightweight-ablation.pdf` | `figure_codes/chap4_lightweight_ablation.py` | ~1.89× | 1×3 |
| [ ] | 中 | `figure/generated/chap5-warning-gen-flow.pdf` | `figure_codes/chap5_warning_gen_flow.py` | ~1.62× | 横向流程，易挤字 |
| [ ] | 中 | `figure/generated/chap5-warning-handle-flow.pdf` | `figure_codes/chap5_warning_handle_flow.py` | ~1.59× | 流程重排 |
| [ ] | 难 | `figure/generated/chap2-ssd-structure.pdf` | `figure_codes/chap2_ssd_structure.py` | ~1.37× | 绝对坐标，要重布 |
| [ ] | 难 | `figure/generated/chap2-program-erase-principle.pdf` | `figure_codes/chap2_program_erase_principle.py` | ~1.62× | 绝对坐标 |
| [ ] | 难 | `figure/generated/chap2-random-forest.pdf` | `figure_codes/chap2_random_forest.py` | ~1.65× | 绝对坐标树 |
| [ ] | 难 | `figure/generated/chap3-tp-tn-fp-fn.pdf` | `figure_codes/chap3_tp_tn_fp_fn.py` | ~1.35× | 绝对坐标示意 |
| [x] | 难 | `figure/generated/chap3-baseline-bar-grid.pdf` | `figure_codes/chap3_baseline_bar_grid.py` | **1.00×** | 已对齐（栏宽出图；FPR 标 ×10⁻⁵ 数值） |
| [ ] | 难 | `figure/generated/chap4-blockfilter-grouping.pdf` | `figure_codes/chap4_blockfilter_grouping.py` | ~1.32× | 绝对坐标 |
| [ ] | 难 | `figure/generated/chap1-framework.pdf` | `figure_codes/chap1_framework.py` | ~2.10× | draw.io 整页重排 |
| [ ] | 难 | `figure/generated/chap3-pipeline.pdf` | `figure_codes/chap3_pipeline.py` | ~2.14× | draw.io |
| [ ] | 难 | `figure/generated/chap3-ensemble.pdf` | `figure_codes/chap3_ensemble.py` | ~6.19× | draw.io，画布过大 |
| [ ] | 难 | `figure/generated/chap5-usecase.pdf` | `figure_codes/chap5_usecase.py` | ~1.71× | draw.io |
| [ ] | 难 | `figure/generated/chap5-software-structure.pdf` | `figure_codes/chap5_software_structure.py` | ~1.61× | draw.io |
| [ ] | 难 | `figure/generated/chap5-database-er.pdf` | `figure_codes/chap5_database_er.py` | ~1.36× | draw.io |

## 汇总

- 易：8（已完成 3 / 已回滚 4 / 余截图 1）
- 中：13
- 难：12（已完成 1）
- 合计：33

## 建议顺序

1. 先做 **易**（快速消掉明显过宽/过窄）
2. 再做 **中**（统一 matplotlib 目标宽约 6.0–6.3 in，并检查字号）
3. 最后做 **难**（绝对坐标图与 draw.io；`chap3-ensemble` 优先排查导出画布）

## 验收

改完后可用：

```bash
python3 -c "
from pathlib import Path
from pypdf import PdfReader
target = 453.54  # pt ≈ 160 mm
for p in sorted(Path('figure/generated').glob('*.pdf')):
    w = float(PdfReader(str(p)).pages[0].mediabox.width)
    print(f'{w/target:5.2f}x  {p.name}')
"
```

理想区间约 **0.90×–1.05×** 栏宽；完成后将上表对应行 `[ ]` 改为 `[x]`。
