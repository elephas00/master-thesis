#!/usr/bin/env bash
# 一键生成秋季盲审 PDF：
#   1) figure_codes/regen_figures.sh
#   2) latexmk
#   3) 用 figure/cover-blind-review.pdf 替换 latex 产物前部封面/独创性声明等，拼出送审稿
#
# 用法（项目根目录）:
#   ./build_blind.sh
#   ./build_blind.sh --skip-figures   # 跳过出图
#   ./build_blind.sh --skip-latex     # 跳过编译（仅重拼封面）
#   ./build_blind.sh --merge-only     # 同 --skip-figures --skip-latex

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

JOBNAME='基于机器学习的固态硬盘故障预测与寿命提升方法研究'
COVER_PDF="${COVER_PDF:-figure/cover-blind-review.pdf}"
LATEX_PDF="out/${JOBNAME}.pdf"
OUT_PDF="${OUT_PDF:-out/${JOBNAME}-秋季盲审.pdf}"

SKIP_FIGURES=0
SKIP_LATEX=0
for arg in "$@"; do
  case "$arg" in
    --skip-figures) SKIP_FIGURES=1 ;;
    --skip-latex)   SKIP_LATEX=1 ;;
    --merge-only)   SKIP_FIGURES=1; SKIP_LATEX=1 ;;
    -h|--help)
      sed -n '2,14p' "$0"
      exit 0
      ;;
    *)
      echo "未知参数: $arg（见 --help）" >&2
      exit 2
      ;;
  esac
done

if [[ ! -f "$COVER_PDF" ]]; then
  echo "缺少盲审前置页: $COVER_PDF" >&2
  echo "应包含：评价标准 + 自评表 + 填好的盲审封面（共 3 页）。" >&2
  exit 1
fi

if [[ "$SKIP_FIGURES" -eq 0 ]]; then
  echo "======== 1/3 重新生成图片 ========"
  bash figure_codes/regen_figures.sh
else
  echo "======== 1/3 跳过出图 ========"
fi

if [[ "$SKIP_LATEX" -eq 0 ]]; then
  echo "======== 2/3 latexmk ========"
  latexmk
else
  echo "======== 2/3 跳过 latexmk ========"
fi

if [[ ! -f "$LATEX_PDF" ]]; then
  echo "找不到编译产物: $LATEX_PDF" >&2
  exit 1
fi

echo "======== 3/3 拼接盲审封面 ========"
python3 - "$COVER_PDF" "$LATEX_PDF" "$OUT_PDF" <<'PY'
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("需要 PyMuPDF：pip3 install pymupdf")

cover_path, latex_path, out_path = sys.argv[1:4]
cover = fitz.open(cover_path)
latex = fitz.open(latex_path)

def page_text(doc, i: int) -> str:
    return doc[i].get_text("text").strip()

# 送审稿用 cover-blind-review.pdf 替换模板自带封面/独创性声明等；
# 从「摘要」前一页空白（若有）起接上 latex 正文，与手工秋季盲审拼法一致。
start = None
for i in range(latex.page_count):
    t = page_text(latex, i)
    first = t.splitlines()[0].strip() if t else ""
    if first == "摘要" or t.startswith("摘要"):
        start = i - 1 if i > 0 and not page_text(latex, i - 1) else i
        break

if start is None:
    sys.exit(f"未在 {latex_path} 中找到「摘要」起始页，无法拼接")

out = fitz.open()
out.insert_pdf(cover)
out.insert_pdf(latex, from_page=start)
out.save(out_path)
n_cover, n_body = cover.page_count, out.page_count - cover.page_count
print(
    f"写入 {out_path}\n"
    f"  前置 {n_cover} 页 ← {cover_path}\n"
    f"  正文 {n_body} 页 ← {latex_path} 第 {start + 1}–{latex.page_count} 页\n"
    f"  合计 {out.page_count} 页"
)
out.close()
cover.close()
latex.close()
PY

echo "完成: $ROOT/$OUT_PDF"
