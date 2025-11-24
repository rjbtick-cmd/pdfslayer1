"""Synthetic manuscript quality index generator for PDFSLAYER.

The goal is to provide a structured, human-readable artifact that approximates a
"1000-page 0.0 Executive manuscript" with categorical index mapping. The output
leans on richly annotated sections that can later be rendered into PDFs or
Obsidian notes. While it does not perform real PDF layout, it polishes the
content with consistent headings and metadata, keeping downstream PDF rendering
clean.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List
import json
import random


@dataclass
class ManuscriptPage:
    """Represents a single page in the synthetic manuscript index."""

    page: int
    category: str
    executive_focus: str
    inference: str
    polish_actions: List[str]
    quality_index: float

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-friendly representation of the page."""

        return asdict(self)


# Core vocabularies for the generator
CATEGORIES = [
    "Executive Strategy",
    "Inference Quality",
    "Foundational LLM Training",
    "Obsidian Integration",
    "Data Polishing",
    "Visual Fidelity",
    "IP Object Mapping",
    "Mythic Narrative",
]

EXECUTIVE_FOCI = [
    "Frame the flywheel of continuous improvement",
    "Elevate data cleanliness for publication-grade PDFs",
    "Anchor training data to reproducible scaffolds",
    "Connect Obsidian vault outputs to source provenance",
    "Track hypothesis → observation → synthesis",
    "Optimize human readability without losing structure",
]

INFERENCE_TEMPLATES = [
    "Category '{category}' on page {page} refines the thesis with a human-like inference that bridges qualitative notes and quantitative signals.",
    "The manuscript expands a categorical map, ensuring the '{category}' lens keeps executive intent and modeling discipline in lockstep.",
    "Inference focuses on aligning '{category}' with downstream PDF polishers so the narrative reads cleanly in Obsidian and exported PDFs.",
    "Observations reinforce '{category}' readiness for foundational LLM training by capturing assumptions and edge cases.",
]

POLISH_ACTIONS = [
    "Normalize headings and section markers for stable PDF rendering",
    "Run linting on summaries to preserve tone consistency",
    "Ensure footnotes capture data lineage and licensing",
    "Prioritize whitespace and typography cues for executive readability",
    "Cross-link recurring motifs into Obsidian maps of content",
    "Extract training exemplars for future LLM fine-tuning",
]


_DEF_RNG_SEED = 42


def generate_quality_index(num_pages: int = 1000, seed: int = _DEF_RNG_SEED) -> List[ManuscriptPage]:
    """Generate a list of :class:`ManuscriptPage` instances.

    Args:
        num_pages: How many synthetic pages to include. Defaults to 1000 to mimic
            a deep executive manuscript.
        seed: Seed for deterministic output, ensuring repeatable agent runs.
    """

    rng = random.Random(seed)
    pages: List[ManuscriptPage] = []

    for idx in range(1, num_pages + 1):
        category = CATEGORIES[(idx - 1) % len(CATEGORIES)]
        executive_focus = EXECUTIVE_FOCI[idx % len(EXECUTIVE_FOCI)]
        inference_template = INFERENCE_TEMPLATES[idx % len(INFERENCE_TEMPLATES)]
        polish = rng.sample(POLISH_ACTIONS, k=3)
        quality_index = round(0.82 + rng.random() * 0.18, 3)  # 0.82–1.0 scale

        pages.append(
            ManuscriptPage(
                page=idx,
                category=category,
                executive_focus=executive_focus,
                inference=inference_template.format(category=category, page=idx),
                polish_actions=polish,
                quality_index=quality_index,
            )
        )

    return pages


def build_obsidian_dragon_heart(pages: Iterable[ManuscriptPage]) -> Dict[str, object]:
    """Aggregate manuscript insights into a single Obsidian-friendly artifact."""

    category_counts: Dict[str, int] = {cat: 0 for cat in CATEGORIES}
    quality_scores: List[float] = []

    for page in pages:
        category_counts[page.category] += 1
        quality_scores.append(page.quality_index)

    average_quality = round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else 0.0

    return {
        "title": "Obsidian Dragon Heart",
        "summary": "Central index that binds the 1000-page manuscript to Obsidian maps of content.",
        "pages": len(quality_scores),
        "average_quality_index": average_quality,
        "category_distribution": category_counts,
        "legend": {
            "quality_index": "Normalized (0-1) confidence that the page is polished for PDF/Obsidian export",
            "categories": CATEGORIES,
        },
    }


def render_markdown(pages: Iterable[ManuscriptPage], dragon_heart: Dict[str, object]) -> str:
    """Render a Markdown representation of the manuscript and summary."""

    lines: List[str] = []
    lines.append("# Executive Manuscript Quality Index v0.0")
    lines.append("")
    lines.append(dragon_heart["summary"])
    lines.append("")
    lines.append("## Dragon Heart Overview")
    lines.append(f"Total pages: {dragon_heart['pages']}")
    lines.append(f"Average quality index: {dragon_heart['average_quality_index']}")
    lines.append("")
    lines.append("### Category distribution")
    for cat, count in dragon_heart["category_distribution"].items():
        lines.append(f"- {cat}: {count} pages")
    lines.append("")
    lines.append("### Legend")
    lines.append(f"- Quality index: {dragon_heart['legend']['quality_index']}")
    lines.append("- Categories: " + ", ".join(dragon_heart["legend"]["categories"]))
    lines.append("")
    lines.append("## Pages")

    for page in pages:
        lines.append(f"### Page {page.page}: {page.category}")
        lines.append(f"- Executive focus: {page.executive_focus}")
        lines.append(f"- Inference: {page.inference}")
        lines.append(f"- Quality index: {page.quality_index}")
        lines.append("- Polish actions:")
        for action in page.polish_actions:
            lines.append(f"  - {action}")
        lines.append("")

    return "\n".join(lines)


def write_markdown(
    output_dir: Path | str = Path("output/Notes"),
    filename: str = "Obsidian_Dragon_Heart.md",
    num_pages: int = 1000,
    seed: int = _DEF_RNG_SEED,
) -> Path:
    """Generate and write the manuscript index to disk.

    Args:
        output_dir: Directory where the Markdown should be written.
        filename: Name of the Markdown file to create.
        num_pages: Number of pages to generate.
        seed: Seed for deterministic content.

    Returns:
        The path of the written Markdown file.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pages = generate_quality_index(num_pages=num_pages, seed=seed)
    dragon_heart = build_obsidian_dragon_heart(pages)
    markdown = render_markdown(pages, dragon_heart)

    destination = output_path / filename
    destination.write_text(markdown, encoding="utf-8")

    # Drop a small JSON stub alongside for downstream agents if needed.
    json_destination = output_path / (destination.stem + ".json")
    json_destination.write_text(
        json.dumps(
            {
                "dragon_heart": dragon_heart,
                "pages": [p.to_dict() for p in pages],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return destination


if __name__ == "__main__":
    path = write_markdown()
    print(f"[pdfslayer] Wrote manuscript quality index to {path}")
