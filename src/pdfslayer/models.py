"""Core PDF data structures for PDFSLAYER.

These lightweight dataclasses mirror the structures referenced in the
README: PdfTextBlock, PdfPage, and PdfDocument. The objects support
summary statistics and JSON-friendly serialization via ``to_dict``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


BBox = Tuple[float, float, float, float]


@dataclass
class PdfTextBlock:
    """A contiguous span of text on a page.

    Attributes:
        text: The raw text content.
        bbox: Optional bounding box in PDF coordinate space
            ``(x0, y0, x1, y1)``.
        metadata: Arbitrary extractor metadata (e.g., font info).
    """

    text: str
    bbox: Optional[BBox] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {"text": self.text, "bbox": self.bbox, "metadata": self.metadata}


@dataclass
class PdfPage:
    """One PDF page worth of text and blocks."""

    index: int
    text: str
    blocks: List[PdfTextBlock] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "index": self.index,
            "text": self.text,
            "blocks": [block.to_dict() for block in self.blocks],
        }


@dataclass
class PdfDocument:
    """Container for an extracted PDF."""

    pages: List[PdfPage] = field(default_factory=list)
    source_path: Optional[str] = None

    def summary(self) -> str:
        word_count = sum(len(page.text.split()) for page in self.pages)
        return f"PdfDocument(pages={len(self.pages)}, words={word_count})"

    def to_dict(self) -> Dict[str, object]:
        return {
            "source_path": self.source_path,
            "pages": [page.to_dict() for page in self.pages],
        }

    @classmethod
    def from_pages(cls, pages: List[PdfPage], source_path: Optional[str] = None) -> "PdfDocument":
        return cls(pages=pages, source_path=source_path)
