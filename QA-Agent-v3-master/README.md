# 🌐 Follow Me

- 🐙 GitHub: https://github.com/Shady1997
- 💼 LinkedIn: https://www.linkedin.com/in/shady-ahmed97/

---

# AI QA Agent — v3

Autonomous QA analysis platform. Reads SRS/BRD/API documents, runs a
multi-agent analysis pipeline on local Ollama LLMs, and publishes
results to Jira as **one Epic per feature with linked test-case tasks**.

---

## What's new in v3

| Area | Improvement |
|---|---|
| ⚡ Parallel | The 6 analyst nodes (risk, security, api, accessibility, performance) run **concurrently** after `requirement_analyst` instead of sequentially — typical wall-clock savings ~50–60% |
| 🎯 Feature-first | New `feature_extractor` node identifies the product features; everything downstream is tagged with its parent feature |
| 🧩 Edge cases | New `edge_case_analyst` node produces a dedicated edge-case report; each edge case becomes a test case tagged `test_type: EdgeCase` |
| 📋 Jira Epics | Publisher now creates **one Epic per feature**, then test-case tasks linked via the `parent` field (with a `Relates` issue-link fallback) |
| 🧠 Dual model | `FAST_MODEL` (default `qwen2.5:3b`) for analysts; `SMART_MODEL` (default `qwen2.5:7b`) for generation and synthesis |
| 📑 Templates | Every prompt now lives in `prompts/*.yaml` with `name / version / model / output_schema / template` — versioned, A/B-testable, no inline prompts in node files |
| 🧪 Structured | Hybrid JSON-first parsing with tolerant text-fallback. New Pydantic models for `Feature`, `EdgeCase`, plus `feature` field on `TestCase` and `Scenario` |
| 🧹 Dedup | Embedding-based cosine similarity deduplication on test cases (default threshold 0.90) — removes near-duplicates the LLM produces |
| 📈 Reports | `features.md`, `edge_cases.md`, expanded `traceability_matrix.md` with feature + Epic columns, plus all v2 artifacts |

---

## Architecture (v3 flow)

```
resources/  (DOCX | PDF | TXT | MD | HTML)
   ↓
markdown/
   ↓
ChromaDB + BM25 (hybrid search)
   ↓
load_documents
   ↓
requirement_analyst                          [FAST_MODEL]
   ↓
   ├── risk_analyst              ───┐
   ├── security_analyst          ───┤
   ├── api_analyst               ───┤  PARALLEL FAN-OUT
   ├── accessibility_analyst     ───┤  (all FAST_MODEL)
   └── performance_analyst       ───┘
   ↓
feature_extractor                            [SMART_MODEL]
   ↓                          (4–12 features detected)
generate_scenarios                           [SMART_MODEL]
   ↓
edge_case_analyst                            [SMART_MODEL]
   ↓
generate_testcases                           [SMART_MODEL]
   ↓                          (LLM tests + edge-case tests, then dedup)
automation_candidate_detector                [free, rule-based]
   ↓
quality_reviewer                             [SMART_MODEL]
   ↓
traceability_matrix                          [free]
   ↓
publish_jira       ── creates 1 Epic per feature
   │                ── then 1 Task (or Xray Test) per test case
   │                   linked to its Epic via `parent` field
   ↓
report_generator
   ↓
outputs/<run_id>/*.md + execution_summary.json
```

---

## Quick start

```bash
# 1. Python 3.11+ and uv
pip install uv

# 2. Pull Ollama models (need both for default config; collapse to one if RAM-limited)
Install Ollama
ollama pull qwen2.5:3b
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
Ollama list

# 3. Create venv + install
uv venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# 4. Configure
cp .env.example .env       # edit Jira creds if publishing

# 5. Drop documents
cp my-srs.docx app/resources/

# 6. Run
python -m app.main
```

After a run, look in `app/outputs/latest/`.

---

## Usage

```bash
# Run the full default flow
python -m app.main

# Force vector DB rebuild
python -m app.main --rebuild

# Analyze one Jira story instead of the SRS
python -m app.main --story "As a user I want OAuth login via Google"

# Help
python -m app.main --help
```

---

## Configuration (.env)

```bash
# Dual-model setup (16GB RAM recommended for defaults)
FAST_MODEL=qwen2.5:3b           # analyst nodes — fast and cheap
SMART_MODEL=qwen2.5:7b          # generation / synthesis nodes — higher quality

# On 8GB RAM? Set both to qwen2.5:3b
# FAST_MODEL=qwen2.5:3b
# SMART_MODEL=qwen2.5:3b

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TEMPERATURE=0

# RAG tuning
RAG_CHUNK_SIZE=1500
RAG_CHUNK_OVERLAP=200

# Test case dedup threshold (0.85 aggressive, 0.90 default, 0.92 conservative)
TC_DEDUP_THRESHOLD=0.90

# Jira (optional — pipeline still runs without these)
JIRA_URL=https://YOUR_DOMAIN.atlassian.net
JIRA_EMAIL=your.email@example.com
JIRA_API_TOKEN=YOUR_TOKEN
JIRA_PROJECT=QA
JIRA_USE_XRAY=0                 # set 1 to create test issues as Xray "Test"
JIRA_EPIC_ISSUETYPE=Epic        # override if your project uses a different name
```

---

## Agent registry (15 agents)

| Agent | Aliases | Tier | Phase | Purpose |
|---|---|---|---|---|
| requirement | `requirement_analyst`, `requirements` | FAST | analyze | Functional analysis, missing/ambiguous detection |
| risk | `risk_analyst`, `risks` | FAST | analyze | Business / regression / integration risks |
| security | `security_analyst` | FAST | analyze | OWASP + authn/authz |
| api | `api_analyst` | FAST | analyze | Endpoints, contracts, status codes |
| accessibility | `accessibility_analyst`, `a11y` | FAST | analyze | WCAG 2.1 + assistive tech |
| performance | `performance_analyst`, `perf` | FAST | analyze | Load / stress / soak / spike |
| **features** | `feature_extractor` | **SMART** | structure | **NEW — top-level capabilities for Epic grouping** |
| scenarios | `generate_scenarios` | SMART | generate | End-to-end QA scenarios (feature-tagged) |
| **edge_cases** | `edge_case_analyst`, `edge` | **SMART** | generate | **NEW — race / state / boundary / timing edge cases** |
| testcases | `generate_testcases`, `tests` | SMART | generate | Structured test cases + dedup |
| automation_candidates | `automation` | free | review | Rule-based automation suitability scoring |
| quality_review | `quality_reviewer` | SMART | review | Critique of generated artifacts |
| traceability | `traceability_matrix` | free | review | Feature → Requirement → Scenario → Test → Jira |
| jira | `publish_jira` | free | publish | Create Epics + linked test issues |
| report | `report_generator` | free | report | Write outputs + execution summary |

---

## Outputs

Every run produces:

```
app/outputs/
├── 20260514_103015/                   # one folder per run
│   ├── requirement_analysis.md
│   ├── risk_analysis.md
│   ├── security_analysis.md
│   ├── api_analysis.md
│   ├── accessibility_analysis.md
│   ├── performance_analysis.md
│   ├── features.md                    # NEW — table of detected features + Epic keys
│   ├── features.json                  # NEW — structured features
│   ├── scenarios.md
│   ├── scenarios_structured.json
│   ├── testcases.md
│   ├── testcases_structured.json
│   ├── edge_cases.md                  # NEW — focused edge-case report
│   ├── edge_cases.json                # NEW
│   ├── quality_review.md
│   ├── automation_candidates.md
│   ├── automation_candidates.json
│   ├── traceability_matrix.md         # now includes Feature + Epic columns
│   ├── traceability_matrix.json
│   └── execution_summary.json         # adds epic_keys, feature_count, dedup counts
└── latest/                            # mirror of the most recent run
```

`execution_summary.json` is suitable for CI ingestion / dashboards.

---

## Node documentation

### Performance Analyst

**Purpose** — Identify load / stress / spike / soak / scalability risks
*before* they hit production.

**Inputs**
- `state.requirement_analysis` (markdown blob from `requirement_analyst`)
- RAG-retrieved chunks filtered to `section_type='performance'`

**Output** (in state.`performance_analysis`) — structured markdown with sections:
- Performance Hot Paths
- Load Test Scenarios
- Stress Test Scenarios
- Spike Test Scenarios
- Soak Test Scenarios
- Scalability Risks
- Suggested KPIs and Thresholds

Each finding includes: hot path, risk, suggested workload, suggested
tool (k6 / JMeter / Gatling / Locust), suggested KPI / threshold.

**QA value** — Functional testing rarely catches performance issues. This node
makes them first-class:

- Flags database hot paths and cache-invalidation traps
- Surfaces third-party API timeout / retry chains
- Calls out queue back-pressure and async worker bottlenecks
- Turns abstract NFRs ("fast") into concrete KPIs ("p95 < 500ms")

Prevents the classic *"it worked in QA, exploded under real load"* outcome.

**Cost** — 1 LLM call on FAST_MODEL (~20–40s on qwen2.5:3b). Runs in parallel
with the other 4 analyst nodes.

---

### Automation Candidate Detector

**Purpose** — Tell the QA team which generated test cases are worth automating
*now*, which should be stabilised first, and which should stay manual.

**Inputs**
- `state.test_cases_structured` (preferred)
- `state.test_cases` (fallback raw text)

**Output** (in state.`automation_candidates`) — list of:

```json
{
  "title": "Verify successful login with valid credentials",
  "score": 0.95,
  "recommendation": "Automate",
  "rationale": ["+ api", "+ validation", "+ regression"]
}
```

**Recommendation tiers**
- `score ≥ 0.75` → **Automate**
- `0.55 ≤ score < 0.75` → **Automate after stabilization**
- `0.35 ≤ score < 0.55` → **Manual first; revisit**
- `score < 0.35` → **Keep manual**

**QA value** — Prevents wasted automation effort. Without this node, teams often:

- Try to automate captcha / 2FA / visual review tests (low ROI)
- Skip automating high-value API regression tests (high ROI)
- Blindly mark every test "automation candidate = Yes"

This node uses domain heuristics to surface the real candidates:

- **Positive signals** (boost score): `api`, `endpoint`, `status code`, `schema`,
  `boundary`, `validation`, `regression`, `json`, `database`, `calculation`,
  `rate limit`
- **Negative signals** (reduce score): `look and feel`, `subjective`,
  `manual inspection`, `exploratory`, `visual review`, `captcha`, `two factor`,
  `third party email`, `physical device`, `real payment`, `human verification`,
  `screen reader`, `accessibility audit`

**Cost** — FREE. Rule-based scoring, no LLM call. Runs in <1 second for
hundreds of test cases.

---

## Jira publishing — how Epic linking works

The publisher runs in two phases:

**Phase 1 — Epics**
For each feature detected by `feature_extractor`, the publisher creates one
issue with `issuetype = "Epic"` (overridable via `JIRA_EPIC_ISSUETYPE`). It
records a `feature_name → epic_key` mapping.

**Phase 2 — Test issues**
For each test case (structured, post-dedup):

1. Looks up the parent Epic key by `test_case.feature`
2. Creates an issue with:
   - `issuetype = "Task"` (or `"Test"` if `JIRA_USE_XRAY=1`)
   - `parent = { "key": <epic_key> }`
   - Priority from `test_case.priority`
   - Labels: `AI_QA`, `Generated`, `AutomationCandidate` (if applicable), `Type_<...>`
3. If Jira rejects the `parent` field (some classic-managed projects do),
   the issue is created without `parent` and a `Relates` issue link is added
   as a fallback so the relationship is still visible.

The result in Jira looks like:

```
EPIC  QA-101  Authentication
├── QA-102  Verify successful login with valid credentials
├── QA-103  Verify error on invalid password
├── QA-104  Verify rate-limit after 5 failed attempts
└── QA-105  [EDGE] Token expires mid-session at submit

EPIC  QA-106  Search
├── QA-107  Verify search returns results for valid query
├── QA-108  Verify empty result message for no matches
└── QA-109  Verify search handles unicode input

EPIC  QA-110  Checkout & Payment
...
```

---

## Project structure

```
qa-agent/
├── app/
│   ├── main.py                       # CLI entry point
│   ├── graph.py                      # LangGraph workflow (parallel fan-out)
│   ├── state.py                      # State shape (adds features, edge_cases, epic_map)
│   ├── llm.py                        # Dual-model client (fast/smart)
│   ├── config/agents.py              # Agent registry + alias resolver
│   ├── converters/convert_to_md.py   # docx/pdf/txt/md/html → markdown
│   ├── jira/client.py                # Lazy JIRA client
│   ├── markdown/                     # Converted markdown files (auto)
│   ├── nodes/
│   │   ├── _common.py                # Shared run_template() helper
│   │   ├── load_documents.py
│   │   ├── requirement_analyst.py    # uses requirement_analyst.yaml
│   │   ├── risk_analyst.py
│   │   ├── security_analyst.py
│   │   ├── api_analyst.py
│   │   ├── accessibility_analyst.py
│   │   ├── performance_analyst.py
│   │   ├── feature_extractor.py      # NEW
│   │   ├── generate_scenarios.py     # feature-aware
│   │   ├── edge_case_analyst.py      # NEW
│   │   ├── generate_testcases.py     # feature-aware + dedup
│   │   ├── automation_candidate_detector.py
│   │   ├── quality_reviewer.py
│   │   ├── traceability_matrix.py    # adds feature + epic columns
│   │   ├── analyze_story.py
│   │   ├── publish_jira.py           # Epic-per-feature, two-phase publish
│   │   └── report_generator.py
│   ├── outputs/                      # Per-run artifacts (auto)
│   ├── prompts_engine/loader.py      # NEW — YAML prompt loader
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── cache.py
│   │   ├── ingest.py                 # chunk_size=1500, 10 categories
│   │   ├── hybrid_retriever.py
│   │   └── bm25_store.py
│   ├── resources/                    # Put SRS/BRD/API docs here
│   ├── router/agent_router.py
│   ├── schemas/__init__.py           # adds Feature, EdgeCase
│   └── utils/
│       ├── logger.py
│       ├── output_writer.py
│       ├── parser.py                 # JSON-first hybrid parser
│       └── dedup.py                  # NEW — embedding-based dedup
├── prompts/                          # NEW — versioned YAML prompts
│   ├── requirement_analyst.yaml
│   ├── risk_analyst.yaml
│   ├── security_analyst.yaml
│   ├── api_analyst.yaml
│   ├── accessibility_analyst.yaml
│   ├── performance_analyst.yaml
│   ├── feature_extractor.yaml
│   ├── generate_scenarios.yaml
│   ├── edge_case_analyst.yaml
│   ├── generate_testcases.yaml
│   ├── quality_reviewer.yaml
│   └── analyze_story.yaml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Editing prompts

Every prompt is a YAML file in `prompts/`:

```yaml
# prompts/requirement_analyst.yaml
name: requirement_analyst
version: 1
model: fast              # 'fast' or 'smart'
output_schema: TextBlob
template: |
  You are a senior QA requirement analyst.
  ...
  Retrieved SRS Context:
  {context}
```

To tune a prompt:

1. Edit the `template:` body
2. Bump `version:` (so you can A/B-test runs)
3. Optionally change `model:` between `fast` and `smart`
4. Re-run — no code change required

Placeholders in `{var_name}` form are substituted from the node's call to
`run_template()`. Missing variables render as empty strings (don't crash).

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Out of memory` from Ollama | Set both models to `qwen2.5:3b`: `FAST_MODEL=qwen2.5:3b` AND `SMART_MODEL=qwen2.5:3b` |
| Vector DB rebuilds every run | Don't pass `--rebuild`; cache lives at `app/rag/vectorstore/` |
| Jira auth fails | Verify `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT` |
| Epics not created, but tasks are | Your project may not support the issue type `Epic` — set `JIRA_EPIC_ISSUETYPE` to whatever your project uses (`Initiative`, `Capability`, etc.) |
| Tasks not linked to Epics | Watch the log: if "Parent field rejected" appears, the publisher fell back to `Relates` links — they're visible under the test issue's "Linked Issues" section |
| `feature_extractor` returns 0 features | The SRS is too short / generic. The node falls back to a single "Core Functionality" feature so the rest of the flow doesn't break |
| Dedup is too aggressive | Raise `TC_DEDUP_THRESHOLD` in `.env` (e.g., `0.92` or `0.95`) |
| `ChatOllama` errors | `ollama serve` must be running; `ollama list` must show both your fast and smart models |

---

## What's deliberately NOT in v3 (still on the roadmap)

These were on the original feedback list but explicitly left for a later pass:

| Item | Why deferred |
|---|---|
| Full Xray test executions / test sets | Xray's API is a separate beast — multi-day project on its own. v3 supports Light Xray (issue type = Test) via `JIRA_USE_XRAY=1` |
| HTML dashboard | Separate frontend concern. The `.json` outputs are dashboard-ready |
| Coverage / hallucination / requirement-coverage metrics | Useful at scale; adding them now without real-world data would be guesswork |
| Async I/O everywhere | Mostly overlaps with parallel execution (which v3 has). Real wins only after JIRA REST round-trips dominate |
| Human review workflow | Out of scope for a local CLI tool — better fit for the future web UI |
| CI/CD pipeline configs | Platform-specific. v3 produces a `execution_summary.json` that any CI can read |

---

## License

@shady-ahmed97 — fork, modify, send a PR.
