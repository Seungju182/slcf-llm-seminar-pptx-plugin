"""
PDF의 figure를 PNG로 캡처. 두 가지 모드 — 전체 페이지 (간단, 권장) 또는 bbox 영역 (정밀).
"""
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pypdfium2",
#   "pdfplumber",
#   "Pillow",
# ]
# ///

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_pdf(pdf_path: str):
    """Open PDF with pypdfium2; raises SystemExit on file-not-found."""
    import pypdfium2 as pdfium

    path = Path(pdf_path)
    if not path.exists():
        sys.exit(f"Error: PDF not found: {pdf_path}")
    return pdfium.PdfDocument(str(path))


def _check_page(doc, page_num: int) -> int:
    """Validate 1-indexed page_num; return 0-indexed index."""
    page_count = len(doc)
    if not (1 <= page_num <= page_count):
        sys.exit(
            f"Error: page {page_num} out of range (PDF has {page_count} page(s))."
        )
    return page_num - 1


def render_page(
    pdf_path: str,
    page_num: int,
    output_path: str,
    scale: float = 2.0,
) -> None:
    """Render a full PDF page (1-indexed) to PNG via pypdfium2."""
    doc = _load_pdf(pdf_path)
    idx = _check_page(doc, page_num)

    page = doc[idx]
    bitmap = page.render(scale=scale, rotation=0)
    pil_image = bitmap.to_pil()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pil_image.save(str(out), format="PNG")
    print(f"Saved page {page_num} -> {out}")


def render_region(
    pdf_path: str,
    page_num: int,
    bbox: tuple[float, float, float, float],
    output_path: str,
    scale: float = 2.0,
) -> None:
    """Render a sub-region of a PDF page to PNG.

    bbox is (x0, y0, x1, y1) in PDF points (72 dpi, origin bottom-left).
    Renders the full page then crops with PIL.
    """
    from PIL import Image

    x0, y0, x1, y1 = bbox
    if x0 >= x1 or y0 >= y1:
        sys.exit(
            f"Error: invalid bbox ({x0},{y0},{x1},{y1}): x0 < x1 and y0 < y1 required."
        )

    doc = _load_pdf(pdf_path)
    idx = _check_page(doc, page_num)
    page = doc[idx]

    page_height = page.get_height()

    bitmap = page.render(scale=scale, rotation=0)
    pil_image = bitmap.to_pil()

    # PDF coords: origin bottom-left; PIL coords: origin top-left
    left = int(x0 * scale)
    upper = int((page_height - y1) * scale)
    right = int(x1 * scale)
    lower = int((page_height - y0) * scale)

    img_w, img_h = pil_image.size
    left = max(0, left)
    upper = max(0, upper)
    right = min(img_w, right)
    lower = min(img_h, lower)

    if right <= left or lower <= upper:
        sys.exit(
            f"Error: bbox ({x0},{y0},{x1},{y1}) produces an empty crop at scale={scale}."
        )

    cropped = pil_image.crop((left, upper, right, lower))
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(str(out), format="PNG")
    print(f"Saved region ({x0},{y0},{x1},{y1}) of page {page_num} -> {out}")


def find_figures(pdf_path: str, page_num: int) -> list[tuple[float, float, float, float]]:
    """Return list of likely-figure bboxes on a page via pdfplumber image detection.

    Each bbox is (x0, y0, x1, y1) in PDF points (72 dpi, origin top-left per pdfplumber).
    """
    import pdfplumber

    path = Path(pdf_path)
    if not path.exists():
        sys.exit(f"Error: PDF not found: {pdf_path}")

    with pdfplumber.open(str(path)) as pdf:
        page_count = len(pdf.pages)
        if not (1 <= page_num <= page_count):
            sys.exit(
                f"Error: page {page_num} out of range (PDF has {page_count} page(s))."
            )
        page = pdf.pages[page_num - 1]
        images = page.images
        return [
            (img["x0"], img["top"], img["x1"], img["bottom"])
            for img in images
        ]


def _parse_bbox(raw: str) -> tuple[float, float, float, float]:
    parts = raw.split(",")
    if len(parts) != 4:
        sys.exit(f"Error: --bbox must be x0,y0,x1,y1 — got: {raw!r}")
    try:
        return tuple(float(p) for p in parts)  # type: ignore[return-value]
    except ValueError:
        sys.exit(f"Error: --bbox values must be numbers — got: {raw!r}")


def _parse_pages(raw: str) -> list[int]:
    try:
        return [int(p.strip()) for p in raw.split(",")]
    except ValueError:
        sys.exit(f"Error: --pages must be comma-separated integers — got: {raw!r}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="extract_figure.py",
        description=(
            "PDF의 figure를 PNG로 캡처.\n"
            "Mode 1 (single): PDF PAGE [--out OUT.png] [--scale 2.0] [--bbox x0,y0,x1,y1]\n"
            "Mode 2 (batch):  PDF --pages 23,45,67 --outdir DIR [--scale 2.0]"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pdf", help="Path to the PDF file.")
    parser.add_argument("page", nargs="?", type=int, help="1-indexed page number (single mode).")
    parser.add_argument("--out", default=None, help="Output PNG path (single mode). Default: page_N.png")
    parser.add_argument("--scale", type=float, default=2.0, help="Render scale (default: 2.0).")
    parser.add_argument("--bbox", default=None, help="Crop region: x0,y0,x1,y1 in PDF points.")
    parser.add_argument("--pages", default=None, help="Comma-separated page numbers (batch mode).")
    parser.add_argument("--outdir", default=".", help="Output directory for batch mode (default: current dir).")

    args = parser.parse_args()

    # Batch mode
    if args.pages is not None:
        page_list = _parse_pages(args.pages)
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        for p in page_list:
            out_path = outdir / f"page_{p:04d}.png"
            render_page(args.pdf, p, str(out_path), scale=args.scale)
        return

    # Single mode
    if args.page is None:
        parser.error("Provide PAGE for single mode, or --pages for batch mode.")

    out_path = args.out or f"page_{args.page}.png"

    if args.bbox is not None:
        bbox = _parse_bbox(args.bbox)
        render_region(args.pdf, args.page, bbox, out_path, scale=args.scale)
    else:
        render_page(args.pdf, args.page, out_path, scale=args.scale)


if __name__ == "__main__":
    main()
