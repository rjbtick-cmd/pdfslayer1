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

## Codex multi-variant output protocol (4-variant rule)
When you explicitly or implicitly ask Codex for **4 versions** of an item (prompt, plan, script, pipeline, spec, etc.), use this behavior template in the system prompt/profile. If no variant count is requested, default to a single optimized answer.

### Global behavior rule
- **Variants 1–3**: three **distinct** takes with different complexity levels, structure, and at least one key design decision.
  - **Version 1 – Simple / Robust**: minimal moving parts; clear steps; few dependencies and assumptions; easy to debug or explain.
  - **Version 2 – Intermediate / Optimized**: adds optimizations/structure; better modularization; readable advanced techniques; practical default.
  - **Version 3 – Advanced / Experimental**: highest sophistication; advanced patterns/heuristics/automation; non-obvious choices; accepts more risk.
- **Variant 4**: **synthesis / best-of** that merges the strongest ideas from 1–3, resolves conflicts, and removes redundancy.

### Synthesis rule for Version 4
- Evaluate 1–3 explicitly (strengths, risks, redundancies).
- Merge only the best ideas:
  - Keep the simplest reliable parts from V1.
  - Keep the most useful optimizations from V2.
  - Keep only the most justified advanced elements from V3.
- Produce a single “optimal for now” design: clearer than V3, more powerful than V1, ready to implement and easy to benchmark against 1–3.

### Required output format
Use this outline exactly when returning 4 variants:

```
[VERSION 1 – SIMPLE / ROBUST]
- Complexity: Low
- Design intent: ...
- Output: 
  <content for version 1>

[VERSION 2 – INTERMEDIATE / OPTIMIZED]
- Complexity: Medium
- Design intent: ...
- Output:
  <content for version 2>

[VERSION 3 – ADVANCED / EXPERIMENTAL]
- Complexity: High
- Design intent: ...
- Output:
  <content for version 3>

[VERSION 4 – SYNTHESIZED OPTIMAL]
- How it uses V1: ...
- How it uses V2: ...
- How it uses V3: ...
- Final output:
  <synthesized best version>
```

Rules:
- Always label each version exactly as above.
- Always include the “Design intent” lines (1–3 sentences) for Versions 1–3.
- In Version 4, explicitly state how each earlier version contributed (even if unused).

### When to apply the rule
Apply this 4-variant protocol when you see phrases like “give 4 versions,” “4 options,” “run this 4 times,” “I want 4 drafts,” or requests for assessment/comparison across multiple versions. Otherwise, return a single optimized response.

## Utility assessment index
Use this rubric to quickly score how useful a plan, prompt, or code snippet is before sharing it. It is designed to be fast (≈60 seconds) and reproducible so multiple reviewers arrive at similar scores.

### Dimensions (0–5 each)
- **Clarity**: The reader can execute the instructions without guessing. 0 = confusing; 5 = crystal clear with unambiguous steps/inputs.
- **Completeness**: Covers prerequisites, steps, and expected outputs. 0 = major gaps; 5 = nothing obvious missing for the stated scope.
- **Actionability**: Specifies concrete actions, commands, or code. 0 = abstract advice; 5 = fully actionable with copy/paste-able snippets.
- **Safety & compliance**: Avoids leaking secrets, respects environment constraints, and calls out risks. 0 = unsafe; 5 = clearly safe and policy-aware.
- **Verification**: Includes ways to validate success (tests, checks, expected logs). 0 = none; 5 = explicit verification steps with pass/fail signals.
- **Efficiency**: Minimizes unnecessary steps, favors defaults, and avoids heavyweight dependencies. 0 = wasteful; 5 = streamlined and pragmatic.

### Scoring
1) Score each dimension 0–5.
2) Compute the **Utility Assessment Index (UAI)**: `UAI = round( (Clarity + Completeness + Actionability + Safety + Verification + Efficiency) / 6 , 2 )`.
3) Record a short rationale (1–2 bullets) for any dimension ≤3 to guide improvements.

**One-minute checklist** (aim for “yes” on all):
- Are prerequisites and inputs stated? (Clarity/Completeness)
- Are there copy/pasteable commands or code? (Actionability)
- Are secret-handling and safety notes explicit? (Safety & compliance)
- Is there a quick verification step with expected outcome? (Verification)
- Is there any obvious waste you can remove? (Efficiency)

### Quick template
```
Utility Assessment
- Clarity: 4 — …
- Completeness: 3 — …
- Actionability: 5 — …
- Safety & compliance: 4 — …
- Verification: 3 — …
- Efficiency: 4 — …

UAI: 3.83 / 5
Rationale: Fill gaps in prerequisites; add a one-line test command.
```

### Usage guidance
- Apply the index to drafts before committing them to the README or sharing with teammates.
- Aim for **UAI ≥ 4.0** for user-facing guides; **≥3.5** is acceptable for internal notes.
- If time is short, score only Clarity, Actionability, and Safety; average those three for a lightweight check.

### CLI calculator (optional)
Run the helper script to compute a score quickly:

```bash
python tools/uai_score.py \
  --clarity 4 --completeness 3.5 --actionability 5 \
  --safety 4 --verification 3 --efficiency 4.5
```

The script prints each dimension, the rounded UAI, and flags any dimensions at or below 3 so you can tighten the draft before sharing.
