"""PDF extraction helpers using pdfplumber.

The loader intentionally emits simple ``PdfDocument`` structures that can be
fed into inference or pattern pipelines. The goal is a transparent, editable
representation rather than a pixel-perfect layout clone.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import pdfplumber

from .models import PdfDocument, PdfPage, PdfTextBlock


def _iter_pages(plumber_pdf: pdfplumber.PDF, max_pages: Optional[int]) -> Iterable[pdfplumber.page.Page]:
    for index, page in enumerate(plumber_pdf.pages):
        if max_pages is not None and index >= max_pages:
            break
        yield page


def extract_text(path: str, max_pages: Optional[int] = None) -> PdfDocument:
    """Extract text into a ``PdfDocument``.

    Args:
        path: Path to the PDF file.
        max_pages: Optional page limit for quick experiments.
    """

    pdf_path = Path(path)
    pages: list[PdfPage] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in _iter_pages(pdf, max_pages):
            text = page.extract_text() or ""
            blocks = _extract_blocks(page)
            pages.append(PdfPage(index=page.page_number - 1, text=text, blocks=blocks))
    return PdfDocument.from_pages(pages, source_path=str(pdf_path))


def _extract_blocks(page: pdfplumber.page.Page) -> list[PdfTextBlock]:
    words = page.extract_words() or []
    if not words:
        return []

    # Greedy grouping by line number keeps implementation simple while ensuring
    # the resulting blocks are meaningful anchors for inference.
    blocks: list[PdfTextBlock] = []
    current_line = words[0]["top"]
    buffer: list[str] = []
    bbox = [words[0]["x0"], words[0]["top"], words[0]["x1"], words[0]["bottom"]]

    for word in words:
        if abs(word["top"] - current_line) > 2.0:
            blocks.append(
                PdfTextBlock(text=" ".join(buffer), bbox=tuple(bbox)),
            )
            buffer = []
            current_line = word["top"]
            bbox = [word["x0"], word["top"], word["x1"], word["bottom"]]

        buffer.append(word["text"])
        bbox[0] = min(bbox[0], word["x0"])
        bbox[1] = min(bbox[1], word["top"])
        bbox[2] = max(bbox[2], word["x1"])
        bbox[3] = max(bbox[3], word["bottom"])

    if buffer:
        blocks.append(PdfTextBlock(text=" ".join(buffer), bbox=tuple(bbox)))

    return blocks
