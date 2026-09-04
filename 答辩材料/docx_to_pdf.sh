#!/usr/bin/env bash
# 将答辩材料中的 Word 修改说明表转为 PDF。
#
# 优先：LibreOffice（soffice）
#   - 临时把 docx 中的「仿宋」替换为 Noto Serif CJK SC（不改原文件）
#   - 依赖本机已安装的 Noto Serif CJK（~/Library/Fonts 或 ~/.local/share/fonts）
#   - 通过 FONTCONFIG_FILE 让 headless 能找到中文字体
# 回退：textutil → HTML → Chrome（版式会偏离原模板）
#
# 用法:
#   ./答辩材料/docx_to_pdf.sh
#   ./答辩材料/docx_to_pdf.sh 工程师学院专业学位研究生学位论文修改说明表.docx
#   ./答辩材料/docx_to_pdf.sh 某文件.docx 某文件.pdf

set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_STEM="工程师学院专业学位研究生学位论文修改说明表"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
FONTCONF="${FONTCONFIG_FILE:-$HOME/.config/fontconfig/fonts.conf}"

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

ensure_fontconfig() {
  mkdir -p "$HOME/.config/fontconfig" "$HOME/.local/share/fonts"
  if [[ ! -f "$FONTCONF" ]]; then
    cat > "$FONTCONF" <<EOF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>$HOME/Library/Fonts</dir>
  <dir>$HOME/.local/share/fonts</dir>
  <dir>/System/Library/Fonts</dir>
  <dir>/System/Library/Fonts/Supplemental</dir>
  <dir>/Library/Fonts</dir>
  <dir>/Applications/LibreOffice.app/Contents/Resources/fonts/truetype</dir>
</fontconfig>
EOF
  fi
  # Prefer a copy under ~/.local/share/fonts for headless fontconfig.
  if [[ -f "$HOME/Library/Fonts/NotoSerifCJK.ttc" && ! -f "$HOME/.local/share/fonts/NotoSerifCJK.ttc" ]]; then
    cp -f "$HOME/Library/Fonts/NotoSerifCJK.ttc" "$HOME/.local/share/fonts/NotoSerifCJK.ttc"
  fi
}

pdf_has_cjk_font() {
  local pdf="$1"
  python3 - "$pdf" <<'PY'
import sys
from pathlib import Path
pdf = Path(sys.argv[1])
try:
    import fitz
    doc = fitz.open(pdf)
except Exception:
    sys.exit(1)
fonts = " ".join(f[3] for page in doc for f in page.get_fonts(full=True)).lower()
ok = any(k in fonts for k in ("noto", "cjk", "song", "hei", "stsong", "source han", "hiragino", "pingfang"))
sys.exit(0 if ok else 1)
PY
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
  local work patched outdir user_inst tmp_pdf
  ensure_fontconfig
  work="$(mktemp -d)"
  # shellcheck disable=SC2064
  trap "rm -rf '$work'" RETURN
  patched="$work/form.docx"
  outdir="$work/out"
  user_inst="$work/user"
  mkdir -p "$outdir" "$user_inst"

  python3 - "$DOCX" "$patched" <<'PY'
import sys, zipfile
src, dst = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.startswith("word/") and item.filename.endswith(".xml"):
            text = data.decode("utf-8")
            text = text.replace("仿宋", "Noto Serif CJK SC").replace("FangSong", "Noto Serif CJK SC")
            data = text.encode("utf-8")
        zout.writestr(item, data)
PY

  FONTCONFIG_FILE="$FONTCONF" FONTCONFIG_PATH="$(dirname "$FONTCONF")" \
    "$soffice" --headless --nologo --nofirststartwizard \
      "-env:UserInstallation=file://$user_inst" \
      --convert-to pdf:writer_pdf_Export \
      --outdir "$outdir" \
      "$patched" >/dev/null

  tmp_pdf="$(find "$outdir" -maxdepth 1 -type f -name '*.pdf' | head -n 1)"
  if [[ -z "$tmp_pdf" || ! -s "$tmp_pdf" ]]; then
    echo "LibreOffice 未生成 PDF" >&2
    return 1
  fi
  if ! pdf_has_cjk_font "$tmp_pdf"; then
    echo "LibreOffice PDF 未嵌入中文字体，改用 Chrome…" >&2
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
  echo "已用 Chrome 写出 $PDF（版式可能偏离原模板）"
}

if SOFFICE="$(find_soffice)"; then
  if ! convert_with_libreoffice "$SOFFICE"; then
    convert_with_chrome
  fi
else
  echo "未找到 LibreOffice，使用 Chrome…" >&2
  convert_with_chrome
fi
