#!/usr/bin/env python3
"""Compile Chinese/English title pages and splice them into the defense PDF.

The English template page overflows onto two pages; the standalone English
tex fits on one page. Both pages are filled with anonymous reviewers and
the actual examining committee.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("需要 PyMuPDF：pip3 install pymupdf")

ROOT = Path(__file__).resolve().parents[1]
CHN_TEX = ROOT / "script" / "title_chn_page.tex"
ENG_TEX = ROOT / "script" / "title_eng_page.tex"
CHN_PDF = ROOT / "figure" / "title-chn.pdf"
ENG_PDF = ROOT / "figure" / "title-eng.pdf"
DEFAULT_TARGET = ROOT / "out" / "基于机器学习的固态硬盘故障预测与寿命提升方法研究-答辩.pdf"
DEFAULT_SYNC = ROOT / "答辩材料" / "学位论文-答辩稿.pdf"


def page_text(doc: fitz.Document, i: int) -> str:
    return doc[i].get_text("text").replace("\u2019", "'")


def is_chn_title_page(text: str) -> bool:
    t = text.strip()
    return "论文作者签名" in t and "答辩委员会" in t


def is_eng_title_page(text: str) -> bool:
    t = text.strip()
    if "独创性声明" in t or "版权使用授权书" in t or "论文作者签名" in t:
        return False
    low = t.lower()
    if "author" in low and "signature" in low:
        return True
    if "examining committee" in low:
        return True
    if "date of oral defence" in low:
        return True
    return False


def compile_tex(tex: Path, jobname: str, dest: Path) -> Path:
    if not tex.exists():
        sys.exit(f"缺少源文件: {tex}")
    logo = ROOT / "figure" / "logo" / "zju.pdf"
    if not logo.exists():
        sys.exit(f"缺少校徽: {logo}")

    out_dir = ROOT / "figure"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-jobname={jobname}",
        f"-output-directory={out_dir}",
        str(tex),
    ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.exit(f"xelatex 编译失败: {tex}")

    if not dest.exists():
        sys.exit(f"编译后未找到 {dest}")
    with fitz.open(dest) as gen:
        n = gen.page_count
    if n != 1:
        sys.exit(f"{dest} 应为 1 页，实际 {n} 页")
    return dest


def remap_links_and_toc(src, out, old_to_new: dict[int, int]) -> tuple[int, int, int]:
    added = skipped = 0
    for src_i, dst_i in old_to_new.items():
        for ln in src[src_i].get_links():
            new_ln = {k: v for k, v in ln.items() if k not in ("xref", "id")}
            kind = new_ln.get("kind")
            if kind in (fitz.LINK_GOTO, fitz.LINK_GOTOR, fitz.LINK_NAMED):
                tgt = new_ln.get("page")
                if tgt is None or tgt not in old_to_new:
                    skipped += 1
                    continue
                new_ln["page"] = old_to_new[tgt]
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
    for lvl, title, page in src.get_toc():
        p0 = page - 1
        if p0 not in old_to_new:
            continue
        new_toc.append([lvl, title, old_to_new[p0] + 1])
    if new_toc:
        out.set_toc(new_toc)
    return added, skipped, len(new_toc)


def splice(src_path: Path, chn_pdf: Path, eng_pdf: Path, dest_path: Path) -> None:
    src = fitz.open(src_path)
    chn = fitz.open(chn_pdf)
    eng = fitz.open(eng_pdf)
    old_total = src.page_count

    out = fitz.open()
    old_to_new: dict[int, int] = {}
    i = 0
    notes = []

    def take_run(pred, start: int) -> int:
        end = start
        for j in range(start + 1, src.page_count):
            if pred(page_text(src, j)):
                end = j
            else:
                break
        return end

    while i < src.page_count:
        t = page_text(src, i)
        if is_chn_title_page(t):
            end = take_run(is_chn_title_page, i)
            out.insert_pdf(chn, from_page=0, to_page=0)
            notes.append(f"中文题名 第 {i + 1}–{end + 1} 页 → 1 页")
            old_to_new[i] = out.page_count - 1
            i = end + 1
            continue
        if is_eng_title_page(t):
            end = take_run(is_eng_title_page, i)
            n = end - i + 1
            next_blank = (
                end + 1 < src.page_count and not page_text(src, end + 1).strip()
            )
            add_blank = i % 2 == 0 and not (n == 1 and next_blank)
            out.insert_pdf(eng, from_page=0, to_page=0)
            old_to_new[i] = out.page_count - 1
            if add_blank:
                blank = fitz.open()
                blank.new_page(width=src[i].rect.width, height=src[i].rect.height)
                out.insert_pdf(blank)
                blank.close()
                notes.append(f"英文题名 第 {i + 1}–{end + 1} 页 → 1 页 + 空白")
            else:
                notes.append(f"英文题名 第 {i + 1}–{end + 1} 页 → 1 页")
            i = end + 1
            continue

        out.insert_pdf(src, from_page=i, to_page=i, links=False, annots=True)
        old_to_new[i] = out.page_count - 1
        i += 1

    added, skipped, n_toc = remap_links_and_toc(src, out, old_to_new)

    tmp = dest_path.with_suffix(".pdf.tmp")
    out.save(tmp, deflate=True, garbage=4)
    new_total = out.page_count
    out.close()
    chn.close()
    eng.close()
    src.close()
    shutil.move(tmp, dest_path)

    print(f"写入 {dest_path}")
    for line in notes:
        print(f"  {line}")
    print(
        f"  页数 {old_total} → {new_total}；链接 {added}（跳过 {skipped}）；书签 {n_toc}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="生成并替换中英文题名页")
    parser.add_argument(
        "pdf",
        nargs="?",
        default=str(DEFAULT_TARGET),
        help="要替换的 PDF（默认答辩稿）",
    )
    parser.add_argument("--skip-compile", action="store_true", help="直接使用已有 figure/title-*.pdf")
    parser.add_argument("--output", help="输出路径；默认覆盖输入 PDF")
    parser.add_argument(
        "--sync",
        action="store_true",
        help="同时复制到 答辩材料/学位论文-答辩稿.pdf",
    )
    args = parser.parse_args()

    target = Path(args.pdf).expanduser().resolve()
    if not target.exists():
        sys.exit(f"找不到 PDF: {target}")

    if args.skip_compile:
        if not CHN_PDF.exists() or not ENG_PDF.exists():
            sys.exit("缺少 figure/title-chn.pdf 或 title-eng.pdf，请先去掉 --skip-compile")
        chn, eng = CHN_PDF, ENG_PDF
    else:
        chn = compile_tex(CHN_TEX, "title-chn", CHN_PDF)
        eng = compile_tex(ENG_TEX, "title-eng", ENG_PDF)

    dest = Path(args.output).expanduser().resolve() if args.output else target
    dest.parent.mkdir(parents=True, exist_ok=True)
    splice(target, chn, eng, dest)

    if args.sync:
        sync_path = DEFAULT_SYNC
        if sync_path != dest:
            shutil.copy2(dest, sync_path)
            print(f"已同步 {sync_path}")


if __name__ == "__main__":
    main()
