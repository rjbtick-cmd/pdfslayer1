"""PDFSLAYER package initialization.

This package hosts utilities for building structured PDF intelligence artifacts
such as manuscript quality indices and Obsidian-friendly exports.
"""

from .manuscript_quality import (
    ManuscriptPage,
    build_obsidian_dragon_heart,
    generate_quality_index,
    render_markdown,
    write_markdown,
)

__all__ = [
    "ManuscriptPage",
    "build_obsidian_dragon_heart",
    "generate_quality_index",
    "render_markdown",
    "write_markdown",
]
