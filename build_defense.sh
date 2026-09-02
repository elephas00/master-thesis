#!/usr/bin/env bash
# 生成答辩版 PDF：
#   用 figure/cover.pdf 的正式封面（单页）替换 latex 产物里会换页的模板封面，
#   保留评阅人页、英文题名页、独创性声明、致谢及之后正文。
#
# 用法（项目根目录）:
#   ./build_defense.sh
#   ./build_defense.sh --skip-figures
#   ./build_defense.sh --skip-latex     # 跳过编译（仅重拼封面）
#   ./build_defense.sh --merge-only     # 同 --skip-figures --skip-latex

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

JOBNAME='基于机器学习的固态硬盘故障预测与寿命提升方法研究'
COVER_PDF="${COVER_PDF:-figure/cover.pdf}"
LATEX_PDF="out/${JOBNAME}.pdf"
OUT_PDF="${OUT_PDF:-out/${JOBNAME}-答辩.pdf}"

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
  echo "缺少正式封面: $COVER_PDF" >&2
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

echo "======== 3/3 拼接正式封面 ========"
python3 - "$COVER_PDF" "$LATEX_PDF" "$OUT_PDF" <<'PY'
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("需要 PyMuPDF：pip3 install pymupdf")

cover_path, latex_path, out_path = sys.argv[1:4]
cover = fitz.open(cover_path)
latex = fitz.open(latex_path)

def page_text(doc, i: int) -> str:
    return doc[i].get_text("text").strip()

# 只用正式封面页，去掉 Word 模板附带的「填写说明」「附件1」。
cover_keep = []
for i in range(cover.page_count):
    t = page_text(cover, i)
    first = t.splitlines()[0].strip() if t else ""
    if first.startswith("填写说明") or first.startswith("附件"):
        continue
    cover_keep.append(i)

if not cover_keep:
    sys.exit(f"{cover_path} 中没有可用封面页")

# 模板封面会拆成两页；从「论文作者签名」的题名页接回 latex。
start = None
for i in range(latex.page_count):
    t = page_text(latex, i)
    if "论文作者签名" in t:
        start = i
        break

if start is None:
    sys.exit(f"未在 {latex_path} 中找到「论文作者签名」题名页，无法拼接")

front = fitz.open()
for i in cover_keep:
    front.insert_pdf(cover, from_page=i, to_page=i)

# 双面印刷：封面为奇数页时补空白，使题名页仍从右页起。
if front.page_count % 2 == 1:
    blank = fitz.open()
    blank.new_page(width=front[0].rect.width, height=front[0].rect.height)
    front.insert_pdf(blank)
    blank.close()

n_front = front.page_count
offset = n_front - start

out = fitz.open()
out.insert_pdf(front)
out.insert_pdf(latex, from_page=start, links=False, annots=True)

added = skipped = 0
for src_i in range(start, latex.page_count):
    dst_i = src_i + offset
    for ln in latex[src_i].get_links():
        new_ln = {k: v for k, v in ln.items() if k not in ("xref", "id")}
        kind = new_ln.get("kind")
        if kind in (fitz.LINK_GOTO, fitz.LINK_GOTOR, fitz.LINK_NAMED):
            tgt = new_ln.get("page")
            if tgt is None or tgt < start:
                skipped += 1
                continue
            new_ln["page"] = tgt + offset
            if kind == fitz.LINK_NAMED:
                new_ln["kind"] = fitz.LINK_GOTO
                new_ln.pop("nameddest", None)
            new_ln.setdefault("to", fitz.Point(0, 0))
            new_ln.setdefault("zoom", 0)
        elif kind != fitz.LINK_URI:
            skipped += 1
            continue
        try:
            out[dst_i].insert_link(new_ln)
            added += 1
        except Exception:
            skipped += 1

new_toc = []
for lvl, title, page in latex.get_toc():
    p0 = page - 1
    if p0 < start:
        continue
    new_toc.append([lvl, title, p0 + offset + 1])
if new_toc:
    out.set_toc(new_toc)

out.save(out_path)
n_body = out.page_count - n_front
print(
    f"写入 {out_path}\n"
    f"  前置 {n_front} 页 ← {cover_path}（封面 {len(cover_keep)} 页"
    + (" + 空白 1 页" if n_front > len(cover_keep) else "")
    + "）\n"
    f"  其后 {n_body} 页 ← {latex_path} 第 {start + 1}–{latex.page_count} 页\n"
    f"  合计 {out.page_count} 页；链接 {added}（跳过 {skipped}）；书签 {len(new_toc)}"
)
out.close()
front.close()
cover.close()
latex.close()
PY

echo "完成: $ROOT/$OUT_PDF"
