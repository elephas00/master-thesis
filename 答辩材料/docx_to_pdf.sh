#!/usr/bin/env bash
# 将答辩材料中的 Word 修改说明表转为 PDF。
# 优先用 LibreOffice（soffice）按原 docx 版式导出；找不到时回退到
# textutil → HTML → Chrome 无头打印（版式会丢）。
#
# 用法（在本目录或仓库根目录）:
#   ./答辩材料/docx_to_pdf.sh
#   ./答辩材料/docx_to_pdf.sh 工程师学院专业学位研究生学位论文修改说明表.docx
#   ./答辩材料/docx_to_pdf.sh 某文件.docx 某文件.pdf

set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_STEM="工程师学院专业学位研究生学位论文修改说明表"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

find_soffice() {
  if command -v soffice >/dev/null 2>&1; then
    command -v soffice
    return
  fi
  local cand
  for cand in \
    /opt/homebrew/bin/soffice \
    /usr/local/bin/soffice \
    /Applications/LibreOffice.app/Contents/MacOS/soffice
  do
    if [[ -x "$cand" ]]; then
      echo "$cand"
      return
    fi
  done
  return 1
}

if [[ $# -eq 0 ]]; then
  DOCX="$DIR/${DEFAULT_STEM}.docx"
  PDF="$DIR/${DEFAULT_STEM}.pdf"
elif [[ $# -eq 1 ]]; then
  DOCX="$1"
  [[ "$DOCX" == /* ]] || DOCX="$DIR/$DOCX"
  PDF="${DOCX%.docx}.pdf"
  PDF="${PDF%.DOCX}.pdf"
elif [[ $# -eq 2 ]]; then
  DOCX="$1"
  PDF="$2"
  [[ "$DOCX" == /* ]] || DOCX="$DIR/$DOCX"
  [[ "$PDF" == /* ]] || PDF="$DIR/$PDF"
else
  echo "用法: $0 [输入.docx] [输出.pdf]" >&2
  exit 2
fi

if [[ ! -f "$DOCX" ]]; then
  echo "找不到 docx：$DOCX" >&2
  exit 1
fi

convert_with_libreoffice() {
  local soffice="$1"
  local outdir tmp_pdf
  outdir="$(mktemp -d)"
  # shellcheck disable=SC2064
  trap "rm -rf '$outdir'" RETURN

  "$soffice" --headless --nologo --nofirststartwizard \
    --convert-to pdf:writer_pdf_Export \
    --outdir "$outdir" \
    "$DOCX" >/dev/null

  tmp_pdf="$(find "$outdir" -maxdepth 1 -type f -name '*.pdf' | head -n 1)"
  if [[ -z "$tmp_pdf" || ! -s "$tmp_pdf" ]]; then
    echo "LibreOffice 未生成 PDF" >&2
    return 1
  fi
  mv -f "$tmp_pdf" "$PDF"
  echo "已用 LibreOffice 写出 $PDF"
}

convert_with_chrome() {
  if [[ ! -x "$CHROME" ]]; then
    echo "未找到 Chrome：$CHROME" >&2
    return 1
  fi

  local tmpdir html
  tmpdir="$(mktemp -d)"
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  html="$tmpdir/form.html"

  textutil -convert html "$DOCX" -output "$html"
  python3 - "$html" <<'PY'
from pathlib import Path
import sys

html_path = Path(sys.argv[1])
html = html_path.read_text(encoding="utf-8")
css = """
    body, p, td, th, div { font-family: "Songti SC", "STSong", "PingFang SC", serif !important; }
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid #000; padding: 6px; vertical-align: top; }
    @page { size: A4; margin: 16mm 14mm; }
    html, body { margin: 0; }
    p.p1 { font-size: 16px; margin: 0 0 12px 0; }
    p.p2, p.p3, p.p5 { font-size: 12px; line-height: 1.55; }
    table.t1 { width: 100%; }
"""
if "</style>" in html:
    html = html.replace("</style>", css + "\n  </style>", 1)
else:
    html = html.replace("<head>", "<head><style>" + css + "</style>", 1)
html_path.write_text(html, encoding="utf-8")
PY

  "$CHROME" \
    --headless=new \
    --disable-gpu \
    --no-pdf-header-footer \
    --print-to-pdf="$PDF" \
    "file://$html" >/dev/null
  echo "已用 Chrome 回退写出 $PDF（版式可能偏离原模板）"
}

if SOFFICE="$(find_soffice)"; then
  convert_with_libreoffice "$SOFFICE"
else
  echo "未找到 LibreOffice，回退 Chrome…" >&2
  convert_with_chrome
fi
