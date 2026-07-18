#!/usr/bin/env bash
# 重新生成 figure_codes/ 下全部出图脚本（排除样式库）
# 用法（项目根目录）:
#   bash figure_codes/regen_figures.sh
#   或: ./figure_codes/regen_figures.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/figure_codes${PYTHONPATH:+:$PYTHONPATH}"

# 按章节排列；thesis_style.py / flowchart_style.py 为共用样式库，不单独运行
SCRIPTS=(
  # 第一章
  chap1_data_grow_trend.py

  # 第二章
  chap2_ssd_structure.py
  chap2_program_erase_principle.py
  chap2_random_forest.py
  chap2_gbdt_graph.py

  # 第三章
  chap3_failure_by_month.py
  chap3_temporal_missing_distribution.py
  chap3_temporal_missing_schematic.py
  chap3_first_jump_pmf.py
  chap3_b_group_mutation_eda.py
  chap3_label_strategy.py
  chap3_tp_tn_fp_fn.py
  chap3_tp_lead_time_test.py
  chap3_baseline_bar_grid.py
  chap3_wk_grid_heatmap.py
  chap3_tp_lead_method_heatmap.py

  # 第四章
  chap4_rimp_by_model_readtype.py
  chap4_lightweight_ablation.py
  chap4_slc_mlc_tlc_vth.py
  chap4_program_erase_comparision.py
  chap4_blockfilter_grouping.py
  chap4_block_labeling_flow.py
  chap4_ensemble_voting_flow.py

  # 第五章
  chap5_warning_gen_flow.py
  chap5_warning_handle_flow.py
  chap5_usecase.py
)

echo "cwd: $ROOT"
echo "PYTHONPATH=$PYTHONPATH"
echo

fail=0
missing=0
for s in "${SCRIPTS[@]}"; do
  if [[ ! -f "figure_codes/$s" ]]; then
    echo "MISSING: figure_codes/$s" >&2
    missing=1
    fail=1
    echo
    continue
  fi
  echo ">>> python3 figure_codes/$s"
  if python3 "figure_codes/$s"; then
    echo
  else
    echo "FAILED: $s" >&2
    fail=1
    echo
  fi
done

if [[ "$fail" -ne 0 ]]; then
  if [[ "$missing" -ne 0 ]]; then
    echo "部分脚本缺失或失败。" >&2
  else
    echo "部分脚本失败。" >&2
  fi
  exit 1
fi
echo "全部完成。输出在 figure/"
