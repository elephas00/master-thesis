"""将论文 PDF 栅格化为灰度预览稿。

默认读取 ``out/基于机器学习的固态硬盘故障预测与寿命提升方法研究.pdf``，
写出 ``out/thesis-gray.pdf``。需已安装 PyMuPDF（``import fitz``）。

用法（项目根目录或任意目录均可）:
    python3 figure_codes/pdf_to_gray.py
    python3 figure_codes/pdf_to_gray.py --dpi 200
    python3 figure_codes/pdf_to_gray.py -i out/foo.pdf -o out/foo-gray.pdf
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = PROJECT_ROOT / "out" / "基于机器学习的固态硬盘故障预测与寿命提升方法研究.pdf"
DEFAULT_DST = PROJECT_ROOT / "out" / "thesis-gray.pdf"


def pdf_to_gray(
    src: Path,
    dst: Path,
    *,
    dpi: int = 150,
) -> Path:
    try:
        import fitz
    except ImportError as e:
        raise SystemExit(
            "需要 PyMuPDF：pip install pymupdf\n"
            f"原始错误: {e}"
        ) from e

    src = src.resolve()
    dst = dst.resolve()
    if not src.is_file():
        raise SystemExit(f"找不到源 PDF: {src}")

    doc = fitz.open(src)
    out = fitz.open()
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    n_pages = len(doc)

    try:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(
                matrix=mat, colorspace=fitz.csGRAY, alpha=False,
            )
            new = out.new_page(width=page.rect.width, height=page.rect.height)
            new.insert_image(new.rect, pixmap=pix)
            if (i + 1) % 20 == 0 or (i + 1) == n_pages:
                print(f"{i + 1}/{n_pages}", flush=True)

        dst.parent.mkdir(parents=True, exist_ok=True)
        out.save(dst, deflate=True)
    finally:
        out.close()
        doc.close()

    return dst


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="论文 PDF → 灰度预览 PDF")
    p.add_argument(
        "-i", "--input", type=Path, default=DEFAULT_SRC,
        help=f"源 PDF（默认: {DEFAULT_SRC.relative_to(PROJECT_ROOT)}）",
    )
    p.add_argument(
        "-o", "--output", type=Path, default=DEFAULT_DST,
        help=f"输出 PDF（默认: {DEFAULT_DST.relative_to(PROJECT_ROOT)}）",
    )
    p.add_argument(
        "--dpi", type=int, default=150,
        help="栅格分辨率（预览 150；更清晰可用 200）",
    )
    args = p.parse_args(argv)

    if args.dpi < 36 or args.dpi > 600:
        raise SystemExit("--dpi 建议在 36–600 之间")

    print(f"src: {args.input}", flush=True)
    print(f"dst: {args.output}", flush=True)
    print(f"dpi: {args.dpi}", flush=True)
    path = pdf_to_gray(args.input, args.output, dpi=args.dpi)
    print(f"wrote {path}", flush=True)


if __name__ == "__main__":
    main()
