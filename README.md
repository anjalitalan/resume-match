# Resume Match

A tool that compares a resume against a job description: it uses the Gemini API to pull
structured information out of both documents, then compares them with deterministic,
rule-based logic — no LLM call decides whether something "matches."

## What it does

1. Takes resume and job description text (typed, pasted, or uploaded as `.txt`).
2. Asks Gemini to extract each into a structured shape: skills, technologies,
   qualifications, and (for the resume) experience entries / (for the job description)
   key requirements.
3. Deterministically compares the two structured results — case/whitespace-insensitive,
   no LLM involved — to find matched and missing skills, technologies, and
   qualifications.
4. Computes a **requirement coverage percentage** from that comparison: the share of the
   job description's listed skills/technologies/qualifications that were also found in
   the resume.
5. Displays all of this in a Streamlit UI, including which job requirements
   (e.g. "3+ years experience") can't be automatically verified at all.

## Architecture

```
resume text ─┐                                                               ┌─► matched / missing (skills,
              ├─► input_handler ─► Gemini extraction ─► ExtractedResume ─┐    │   technologies, qualifications)
job desc text─┘   (validation)     (structured output)  ExtractedJD    ─┴─► matcher ─► MatchResult ─► scorer ─► ScoreResult
                                                                                                                       │
                                                                                                    Streamlit UI (app.py) ◄┘
                                                                                                    (presentation only)
```

Each stage is an independent, independently-tested Python module:

| Layer | Module | Responsibility |
|---|---|---|
| Input handling | `resume_match/input_handler.py` | Validates raw text (non-empty, under a length cap) |
| Extraction | `resume_match/extraction/` | Calls Gemini with a JSON schema to get structured data back |
| Matching | `resume_match/matching/` | Deterministic, LLM-free comparison of the structured data |
| Scoring | `resume_match/scoring/` | Deterministic coverage percentage from the match result |
| Orchestration | `resume_match/analysis.py` | Wires the above into a single `analyze()` call |
| Evaluation | `evaluation/` | Hand-written input/output cases for the matcher and scorer, used by both pytest and a standalone summary script |
| Presentation | `app.py` | Streamlit UI; calls `analyze()` and renders the result — contains no matching/scoring logic itself |

Gemini is used **only** for turning unstructured text into structured data. Everything
after that — matching, scoring — is plain Python and fully deterministic: the same
inputs always produce the same output, and it's unit-testable without any network call.

## Technology stack

- Python 3.12
- [`google-genai`](https://pypi.org/project/google-genai/) — official Gemini API client
- `pydantic` — schema definitions, used directly as Gemini's structured-output schema
- `streamlit` — UI
- `python-dotenv` — loads the API key from `.env`
- `pytest` — test suite

## Setup

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt      # Windows
# source venv/bin/activate && pip install -r requirements.txt   # macOS/Linux
```

Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey),
then:

```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```

Edit `.env` and set:

```
GEMINI_API_KEY=your_key_here
```

`.env` is git-ignored — never commit it.

## Running the app

```bash
venv\Scripts\streamlit run app.py
```

Open the URL Streamlit prints (default `http://localhost:8501`). You can paste text
directly, upload a `.txt` file, or click "Use sample resume / job description" to try
it with the bundled examples in `samples/`.

## Running the tests

```bash
venv\Scripts\python -m pytest -q
```

All 47 tests are deterministic and mock the Gemini client — `pytest` never makes a live
API call (enforced by `pytest.ini`, which scopes discovery to `tests/` only; the
manual, live-call sanity scripts `test_gemini.py`, `test_input_handler.py`, and
`test_extraction.py` at the repo root are intentionally outside that scope).

For a plain-language pass/fail summary of the hand-written evaluation cases:

```bash
venv\Scripts\python -m evaluation.report
```

## How extraction works

Gemini is called with `response_schema` set to a Pydantic model
(`ExtractedResume` / `ExtractedJobDescription`), and `response_mime_type` set to
`application/json`. The SDK validates Gemini's JSON output against that schema and
hands back an actual Python object (`response.parsed`) — there's no manual JSON
parsing or regex-scraping of free-text output. If Gemini's response fails to validate,
or the API call itself fails (including transient errors and network timeouts), it's
raised as a single `ExtractionError` rather than leaking a raw SDK exception.

The prompts explicitly instruct the model to return an empty list rather than invent a
placeholder when a category has no relevant information in the source text, and both
schemas strip blank/whitespace-only list entries as a defensive measure.

## How matching works

Matching is category-to-category and purely deterministic — no API calls:

- `skills`, `technologies`, and `qualifications` exist on both the resume and job
  description schemas, so each is compared directly against its counterpart.
- Normalization is deliberately conservative: lowercase, trimmed, internal whitespace
  collapsed. No stemming, no punctuation stripping, no synonym mapping — `Python` and
  `python` match; `JS` and `JavaScript` do not.
- `key_requirements` (e.g. "3+ years experience", "Bachelor's degree") only exists on
  the job description side — there's no resume field to compare it against — so it's
  never guessed at. It's surfaced as a separate list of items to check manually.

**Known limitation:** matching only happens within a category. If Gemini extracts
"Flask" under the resume's `skills` but the job description's `technologies`, they will
not be counted as a match. This is intentional (avoiding speculative cross-category or
semantic matching) and is covered by a dedicated test/evaluation case, not a silent gap.

## How coverage is calculated

```
total_required = unique(skills required) + unique(technologies required) + unique(qualifications required)
total_matched  = unique(skills matched)  + unique(technologies matched)  + unique(qualifications matched)

coverage_percent = round(100 * total_matched / total_required)   if total_required > 0
coverage_percent = None                                          if total_required == 0
```

Duplicate items (the same skill listed twice in a job description) are counted once,
so they can't inflate the score. `key_requirements` is excluded from this percentage
entirely for the reason above.

**This number is a text-overlap measure, not a job-fit score.** It says nothing about
experience depth, proficiency, soft skills, or whether someone would actually succeed
in the role — the UI states this explicitly next to the number, and the app never
labels it "match score" or "fit score" for that reason.

## Limitations

- Extraction quality depends on Gemini's categorization, which is not guaranteed
  consistent between the resume and job description (see the matching limitation
  above).
- No semantic or synonym matching — abbreviations, alternate spellings, and related
  technologies are treated as distinct strings.
- Text input only; no PDF/DOCX parsing.
- No persistence — each analysis is independent; nothing is saved between runs.
- The public Gemini API occasionally returns transient `503` errors under high demand;
  the app surfaces this as a clear error message rather than retrying automatically or
  crashing, but the user may need to click "Analyze" again.
- Evaluated only against a small, hand-written set of deterministic cases
  (`evaluation/`) and one manually reviewed resume/job description sample — not a
  large or blind test set.

## Project structure

```
resume_match/           Core library (no Streamlit dependency)
  input_handler.py       Text validation
  gemini_client.py        Gemini client + model constant
  analysis.py             extract -> match -> score orchestration
  extraction/              Gemini-backed structured extraction
  matching/                 Deterministic comparison
  scoring/                   Deterministic coverage calculation
evaluation/              Hand-written input/output cases + summary script
tests/                   pytest suite (mirrors resume_match/ layout)
samples/                 Example resume/job description text for the UI and tests
app.py                   Streamlit UI
```
