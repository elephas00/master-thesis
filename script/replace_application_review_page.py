#!/usr/bin/env python3
"""用「硕士学位答辩申请审核材料」单页替换学位申请书里的导师评语页。

`按交件顺序/01-学位申请书.pdf` 是指向
`22360325-龙泳江申请表_1788356704198.pdf` 的软链。默认覆盖该 PDF，
软链会一并更新。

定位规则：找到「论文答辩委员会对论文的评语和表决结果」页，取其前一页。
无论该页仍是 Excel 转出的文字，还是已经换成扫描件，都可重复执行。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("需要 PyMuPDF：pip3 install pymupdf")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APP = ROOT / "答辩材料" / "22360325-龙泳江申请表_1788356704198.pdf"
DEFAULT_REVIEW = ROOT / "答辩材料" / "硕士学位答辩申请审核材料.pdf"
DEFENSE_MARKER = "论文答辩委员会对论文的评语和表决结果"


def page_text(doc: fitz.Document, i: int) -> str:
    return (doc[i].get_text("text") or "").strip()


def find_review_page(doc: fitz.Document, page_arg: int | None) -> int:
    if page_arg is not None:
        idx = page_arg - 1
        if idx < 0 or idx >= doc.page_count:
            sys.exit(f"页码 {page_arg} 超出范围（共 {doc.page_count} 页）")
        return idx

    hits = [
        i
        for i in range(doc.page_count)
        if DEFENSE_MARKER in page_text(doc, i)
    ]
    if not hits:
        sys.exit(f"未找到含「{DEFENSE_MARKER}」的页，无法定位导师评语页")
    if hits[0] == 0:
        sys.exit("答辩委员会页是第 1 页，没有可替换的前一页")
    return hits[0] - 1


def fit_rect(src: fitz.Rect, dst: fitz.Rect) -> fitz.Rect:
    scale = min(dst.width / src.width, dst.height / src.height)
    w, h = src.width * scale, src.height * scale
    x0 = dst.x0 + (dst.width - w) / 2
    y0 = dst.y0 + (dst.height - h) / 2
    return fitz.Rect(x0, y0, x0 + w, y0 + h)


def splice(app_path: Path, review_path: Path, dest_path: Path, page_arg: int | None) -> None:
    app = fitz.open(app_path)
    review = fitz.open(review_path)
    if review.page_count < 1:
        sys.exit(f"{review_path} 是空 PDF")

    idx = find_review_page(app, page_arg)
    dst_rect = app[idx].rect
    src_rect = review[0].rect

    out = fitz.open()
    for i in range(app.page_count):
        if i != idx:
            out.insert_pdf(app, from_page=i, to_page=i, links=False, annots=True)
            continue
        page = out.new_page(width=dst_rect.width, height=dst_rect.height)
        page.show_pdf_page(fit_rect(src_rect, dst_rect), review, 0)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest_path.with_suffix(".pdf.tmp")
    out.save(tmp, deflate=True, garbage=4)
    n = out.page_count
    out.close()
    review.close()
    app.close()
    shutil.move(tmp, dest_path)

    print(f"写入 {dest_path}")
    print(f"  第 {idx + 1} 页 ← {review_path.name}（共 {n} 页）")


def main() -> None:
    parser = argparse.ArgumentParser(description="用审核材料页替换学位申请书导师评语页")
    parser.add_argument(
        "pdf",
        nargs="?",
        default=str(DEFAULT_APP),
        help="学位申请书 PDF（默认 22360325-龙泳江申请表_1788356704198.pdf）",
    )
    parser.add_argument(
        "--review",
        default=str(DEFAULT_REVIEW),
        help="替换用的单页 PDF（默认 硕士学位答辩申请审核材料.pdf）",
    )
    parser.add_argument("--output", help="输出路径；默认覆盖输入 PDF")
    parser.add_argument("--page", type=int, help="手动指定要替换的页码（从 1 起）")
    args = parser.parse_args()

    app_path = Path(args.pdf).expanduser().resolve()
    review_path = Path(args.review).expanduser().resolve()
    if not app_path.exists():
        sys.exit(f"找不到申请书 PDF: {app_path}")
    if not review_path.exists():
        sys.exit(f"找不到审核材料 PDF: {review_path}")

    dest = Path(args.output).expanduser().resolve() if args.output else app_path
    splice(app_path, review_path, dest, args.page)


if __name__ == "__main__":
    main()
