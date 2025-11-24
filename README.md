# pdfslayer

PDF parsing and inference graph playground. The goal is to turn PDFs into structured objects (PdfDocumentAST), reason about their claims (InferenceGraph), map higher-level recurrences (PatternGraph), and capture reusable IP objects.

## Layout
- `src/pdfslayer/`
  - `pdf_loader.py` — PDF ingestion and text extraction into `PdfDocument`.
  - `models.py` — PdfDocument/PdfPage/PdfTextBlock structures.
  - `inference.py` — nodes/edges for inference graphs plus JSON serialization.
  - `patterns.py` — pattern graphs, frameworks, and theoretical indexing helpers.

## Quick start
1) Install Python 3.10+.
2) Install deps (PyPDF2 is optional but required for extraction):
   ```bash
   pip install -r requirements.txt
   ```
   Or install the package in editable mode:
   ```bash
   pip install -e .
   ```
3) Extract text from a PDF:
   ```bash
   python - <<'PY'
   from pdfslayer.pdf_loader import extract_text
   doc = extract_text("example.pdf", max_pages=2)
   print(doc.summary())
   print(doc.to_dict()["pages"][0]["text"][:400])
   PY
   ```
   If `python` isn’t on PATH, try `py` instead (e.g., `py python/test_parse.py <file.pdf>`).

## Concepts
- **PdfDocumentAST**: captures pages/blocks/text with metadata. `PdfDocument.to_dict()` → JSON-friendly.
- **InferenceGraph**: nodes (`Claim`, `Assumption`, `Implication`, `Analogy`, `Tension`) and edges (`supports`, `contradicts`, `parallels`, `implies`). Build with `InferenceGraph.add_node/add_edge`, serialize with `to_dict()`.
- **PatternGraph**: links patterns to inference nodes (anchors). Useful for spotting recurring structures.
- **IP Objects**: reusable frameworks/taxonomies/algorithms stored alongside pattern graphs.

## Minimal inference graph usage
```python
from pdfslayer.inference import InferenceGraph, NodeType, EdgeType

graph = InferenceGraph()
n1 = graph.add_node(kind=NodeType.CLAIM, content="Solar adoption cuts peak load.")
n2 = graph.add_node(kind=NodeType.ASSUMPTION, content="Peak load happens mid-day.")
graph.add_edge(src=n2.id, dst=n1.id, kind=EdgeType.SUPPORTS, rationale="Assumption supports claim.")
print(graph.to_dict())
```

## Interweave the theoretical indexing framework
```python
from pdfslayer.inference import InferenceGraph, NodeType
from pdfslayer.patterns import build_theoretical_indexing_framework, weave_theoretical_indexing

graph = InferenceGraph()
graph.add_node(NodeType.CLAIM, "Solar adoption cuts peak load.")
graph.add_node(NodeType.ASSUMPTION, "Peak load happens mid-day.")
graph.add_node(NodeType.IMPLICATION, "Utilities should stagger pricing signals.")

framework = build_theoretical_indexing_framework()
placement = weave_theoretical_indexing(graph)
print(framework.to_dict())
print({step: [node.id for node in nodes] for step, nodes in placement.items()})
```

## Minimal pattern/IP usage
```python
   from pdfslayer.patterns import PatternGraph, Pattern, Framework
   
   pg = PatternGraph()
   pg.add_pattern(Pattern(name="Virtuous cycle", description="Positive feedback loop", anchors=[]))
   pg.frameworks.append(Framework(name="Adoption Flywheel", steps=["Awareness","Trial","Advocacy"]))
   print(pg.to_dict())
   ```
   
## Easiest way to run (Windows, no typing)
1) Drop PDFs into `pdfs/` (folder created at repo root).
2) Double-click `run_all_pdfs.bat`.
   - If you set `OBSIDIAN_VAULT` in `.env`, outputs go to `<vault>/Notes/`.
   - If not set, outputs go to `<repo>/output/Notes/`.
3) Find `*-extract.json` and `*-extract.md` in the Notes folder.

## Testing
The repo is dependency-light; no test runner is wired yet. Add pytest-based tests under `tests/` for future work.
