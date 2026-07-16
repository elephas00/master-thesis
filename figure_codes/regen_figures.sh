#!/usr/bin/env bash
# 重新生成第三、四章定量图（使用 figure_codes/thesis_style.py）
# 用法（项目根目录）:
#   bash figure_codes/regen_figures.sh
#   或: ./figure_codes/regen_figures.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/figure_codes${PYTHONPATH:+:$PYTHONPATH}"

SCRIPTS=(
  chap3_failure_by_month.py
  chap3_temporal_missing_distribution.py
  chap3_temporal_missing_schematic.py
  chap3_first_jump_pmf.py
  chap3_b_group_mutation_eda.py
  chap3_tp_lead_time_test.py
  chap3_baseline_bar_grid.py
  chap3_wk_grid_heatmap.py
  chap3_tp_lead_method_heatmap.py
  chap4_rimp_by_model_readtype.py
  chap4_lightweight_ablation.py
  chap4_bar_chart.py
  chap4_slc_mlc_tlc_vth.py
)

echo "cwd: $ROOT"
echo "PYTHONPATH=$PYTHONPATH"
echo

fail=0
for s in "${SCRIPTS[@]}"; do
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
  echo "部分脚本失败。" >&2
  exit 1
fi
echo "全部完成。输出在 figure/"
