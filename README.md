# pdfslayer

PDF parsing and inference graph playground. The goal is to turn PDFs into structured objects (PdfDocumentAST), reason about their claims (InferenceGraph), map higher-level recurrences (PatternGraph), and capture reusable IP objects.

## Layout
- `src/pdfslayer/`
  - `pdf_loader.py` — PDF ingestion and text extraction into `PdfDocument`.
  - `models.py` — PdfDocument/PdfPage/PdfTextBlock structures.
  - `inference.py` — nodes/edges for inference graphs plus JSON serialization.
  - `patterns.py` — pattern graphs and IP object schemas.

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

## Windows shell notes (PowerShell 7 vs. CMD)
- The one-click `.bat` helpers run in **CMD**, but if you need to run Python/Node commands manually, open **PowerShell 7** (prompt shows `PS`). If you see `C:\...>` without `PS`, you are still in CMD.
- Quick launch: press **Win + X → Windows PowerShell (Admin)** or run `pwsh` from Start. Confirm with `$PSVersionTable.PSVersion.Major` returning `7`.
- Staying in CMD hides helpers such as `$env:` variables or `pm2`. Switch shells before running the commands below.
- Example PowerShell setup for running a local orchestrator (no Docker):
  ```powershell
  cd C:\Users\<you>\Desktop\pdfslayer\dragon-grid
  $env:PYTHONPATH = "$PWD"
  $env:USE_LOCAL_WORKER = "1"
  python -m dragon_grid.orchestrator
  ```
- To use Docker mode instead (PowerShell):
  ```powershell
  cd C:\Users\<you>\Desktop\pdfslayer\dragon-grid
  $env:PYTHONPATH = "$PWD"
  $env:USE_LOCAL_WORKER = ""
  docker --version   # ensure Docker is on PATH
  docker build -f Dockerfile.worker -t dragon-grid-worker:latest .
  python -m dragon_grid.orchestrator
  ```
- Adding `pm2` to PATH from PowerShell:
  ```powershell
  $env:Path += ";$env:APPDATA\npm"
  pm2 -v
  ```
- Reminder: the built-in `python -m http.server` replies `501` on POST; that’s expected because it only serves static files. Use the orchestrator/backend for API requests.

## Testing
The repo is dependency-light; no test runner is wired yet. Add pytest-based tests under `tests/` for future work.

## Cloud-first (hands-off) pipeline
If you want the pipelines to run without keeping your PC on, you can deploy a small worker to Google Cloud Platform. Adapt the commands for AWS/Azure if preferred.

- **Storage**: single bucket with clear prefixes (e.g., `gs://automa-datasets/raw/`, `processed/`, `embeddings/`).
- **Secrets**: use Secret Manager for credentials (e.g., `OPENAI_API_KEY`).
- **Compute**: one Dockerized Python worker running on Cloud Run.
- **Automation**: Cloud Scheduler → Pub/Sub → Cloud Run job trigger every 10 minutes (or your cadence).

### One-time setup commands (GCP)
Run these from a machine with the gcloud CLI authenticated to your project:

```bash
# Storage bucket
gcloud storage buckets create gs://automa-datasets --location=us-central1
gcloud storage cp --recursive "C:\path\to\data" gs://automa-datasets/raw/

# Secrets
gcloud secrets create OPENAI_API_KEY --replication-policy="automatic"
echo YOUR_KEY | gcloud secrets versions add OPENAI_API_KEY --data-file=-

# Build & deploy worker (from the folder containing Dockerfile)
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/automa-worker
gcloud run deploy automa-worker \
  --image gcr.io/$(gcloud config get-value project)/automa-worker \
  --region us-central1 \
  --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest \
  --allow-unauthenticated  # tighten with IAM if desired

# Scheduler (every 10 minutes)
gcloud scheduler jobs create http run-automa \
  --schedule="*/10 * * * *" \
  --uri="https://<your-cloud-run-url>/run-pipeline" \
  --http-method=POST
```

### Worker outline
- Read input blobs from `gs://automa-datasets/raw/`.
- Call the LLM using `OPENAI_API_KEY` from Secret Manager.
- Write results to `gs://automa-datasets/processed/` (add `embeddings/` later if needed).

### When you need your PC
Only for editing code, running `gcloud run deploy`, and checking logs. All processing runs in Cloud Run on the schedule you set.
