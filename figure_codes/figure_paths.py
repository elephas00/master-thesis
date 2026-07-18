"""方案 B：生成物路径约定。

- figure_codes/_build/     draw.io 中间 XML（gitignore）
- figure/generated/        脚本输出 PDF（gitignore）
- figure/                  仅静态资源（logo、截图、rules 等）
"""

from __future__ import annotations

from pathlib import Path

FIGURE_CODES_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FIGURE_CODES_DIR.parent
BUILD_DIR = FIGURE_CODES_DIR / "_build"
GENERATED_DIR = PROJECT_ROOT / "figure" / "generated"


def ensure_output_dirs() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
