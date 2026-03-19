# Before & After: Triage Skill Refactor

A real example of refactoring an AI triage skill from prose-only LLM chains to D-P-D architecture.

---

## What the Skill Does

Takes a batch of unstructured text captures (ideas, tasks, notes, links) and:
1. Parses them into structured items
2. Classifies each item by type and priority
3. Routes each item to the correct destination (task queue, content pipeline, archive)
4. Generates a summary report

---

## Before: 4 Chained P Steps

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  P: Parse │────>│ P: Class │────>│ P: Route │────>│ P: Report│
│  raw text │     │  ify     │     │  items   │     │  summary │
└──────────┘     └──────────┘     └──────────┘     └──────────┘

Reliability: 0.9 × 0.9 × 0.9 × 0.9 = 65.6%
```

### Problems

- **All logic lived in SKILL.md prose.** One giant prompt with instructions for all 4 steps.
- **No structured output.** The LLM returned markdown tables that had to be parsed with regex.
- **P-P-P-P chain.** Four probabilistic steps with zero validation between them.
- **Silent failures.** When classification was wrong, routing was wrong, but the summary looked fine.
- **No telemetry.** No way to know which step failed or how often.

### The SKILL.md (Before)

```markdown
# Triage

Take all the captures below and:
1. Parse each one into a separate item
2. Classify each as: task, content-idea, reference, or junk
3. Route tasks to the task queue, content to the content pipeline,
   reference to the archive, junk to trash
4. Give me a summary table of what you did

Here are the captures:
{raw_captures}
```

### Failure Modes

- LLM merges two captures into one item (parsing error)
- LLM classifies a task as a content-idea (classification error)
- LLM skips routing entirely and just gives the summary (routing error)
- LLM invents items that weren't in the input (hallucination)
- No way to detect any of these without manual review

---

## After: D-P-D Chain

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ D: Parse │────>│ P: Class │────>│ D: Valid  │────>│ D: Route │────>│ D: Report│
│  input   │     │  ify     │     │  ate     │     │  items   │     │  + log   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘

Reliability: 1.0 × 0.9 × 1.0 × 1.0 × 1.0 = 90%
```

**One P step. Four D steps. 90% reliability instead of 65.6%.**

### The Architecture

```
triage/
├── SKILL.md                  <- P: classification prompt only
└── scripts/
    ├── parse_input.py        <- D: split raw text into items
    ├── validate_classification.py  <- D: check LLM output
    └── route_items.py        <- D: deterministic routing + report
```

### Step 1: Parse Input [D] — `parse_input.py`

No LLM needed. Split raw captures by delimiter, extract metadata, produce structured JSON.

```python
def parse_captures(raw_text: str) -> list[dict]:
    """Split raw captures into structured items."""
    items = []
    for i, block in enumerate(raw_text.split("---")):
        block = block.strip()
        if not block:
            continue
        items.append({
            "id": f"capture-{i+1:03d}",
            "raw_text": block,
            "char_count": len(block),
            "has_url": "http" in block.lower(),
            "has_date": bool(re.search(r"\d{4}-\d{2}-\d{2}", block)),
        })
    return items
```

**Output:**
```json
{
  "items": [
    {
      "id": "capture-001",
      "raw_text": "Build a dashboard for tracking outbound metrics",
      "char_count": 48,
      "has_url": false,
      "has_date": false
    },
    {
      "id": "capture-002",
      "raw_text": "Great thread on AI agent reliability https://example.com/thread",
      "char_count": 63,
      "has_url": true,
      "has_date": false
    }
  ],
  "metadata": {
    "count": 2,
    "timestamp": "2026-03-15T14:30:00Z"
  }
}
```

### Step 2: LLM Classification [P] — `SKILL.md`

The ONLY probabilistic step. Classify each item. Return structured JSON.

```markdown
Classify each item into exactly one category:
- task: An actionable work item
- content_idea: A topic worth writing about
- reference: Useful information to save
- junk: Not worth keeping

For each item, return:
- id (must match the input id exactly)
- classification (one of the four categories above)
- confidence (0.0 to 1.0)
- reasoning (one sentence explaining why)
```

**Required output:**
```json
{
  "classifications": [
    {
      "id": "capture-001",
      "classification": "task",
      "confidence": 0.95,
      "reasoning": "Contains an actionable directive: 'Build a dashboard'"
    },
    {
      "id": "capture-002",
      "classification": "reference",
      "confidence": 0.88,
      "reasoning": "Contains a URL to external content worth saving"
    }
  ]
}
```

### Step 3: Validate Classification [D] — `validate_classification.py`

Check every aspect of the LLM output before proceeding.

```python
VALID_CLASSIFICATIONS = {"task", "content_idea", "reference", "junk"}

def validate(input_items: list[dict], classifications: list[dict]) -> list[dict]:
    errors = []

    # Check all input items have a classification
    input_ids = {item["id"] for item in input_items}
    output_ids = {c["id"] for c in classifications}

    missing = input_ids - output_ids
    if missing:
        errors.append(f"Missing classifications for: {missing}")

    extra = output_ids - input_ids
    if extra:
        errors.append(f"Hallucinated items not in input: {extra}")

    for c in classifications:
        # Enum check
        if c["classification"] not in VALID_CLASSIFICATIONS:
            errors.append(f"{c['id']}: invalid classification '{c['classification']}'")

        # Confidence range
        if not (0.0 <= c.get("confidence", 0) <= 1.0):
            errors.append(f"{c['id']}: confidence out of range")

        # Required fields
        if not c.get("reasoning"):
            errors.append(f"{c['id']}: missing reasoning")

    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")

    return classifications
```

### Step 4: Route Items [D] — `route_items.py`

Pure deterministic routing based on validated classifications.

```python
ROUTES = {
    "task":         "task_queue",
    "content_idea": "content_pipeline",
    "reference":    "archive",
    "junk":         "trash",
}

def route(classifications: list[dict]) -> dict:
    results = []
    for item in classifications:
        destination = ROUTES[item["classification"]]
        # Write to appropriate destination...
        results.append({
            "id": item["id"],
            "routed_to": destination,
            "status": "completed",
        })

    # Generate deterministic summary
    summary = {}
    for r in results:
        dest = r["routed_to"]
        summary[dest] = summary.get(dest, 0) + 1

    return {"results": results, "summary": summary}
```

**Output:**
```json
{
  "results": [
    {"id": "capture-001", "routed_to": "task_queue", "status": "completed"},
    {"id": "capture-002", "routed_to": "archive", "status": "completed"}
  ],
  "summary": {
    "task_queue": 1,
    "archive": 1
  }
}
```

---

## Key Differences

| Aspect | Before | After |
|--------|--------|-------|
| P steps | 4 | 1 |
| D steps | 0 | 4 |
| Reliability | 65.6% | 90% |
| Output format | Markdown table | Structured JSON |
| Validation | None | Schema + enum + range + hallucination check |
| Telemetry | None | Every step logged |
| Debugging | Re-read entire LLM output | Check specific step that failed |
| Hallucination detection | Manual review | Automatic (input ID matching) |

---

## Lessons Learned

1. **Parsing is almost never a P problem.** If the input has any structure at all (delimiters, headers, dates), code can parse it more reliably than an LLM.

2. **Routing is always a D problem.** Once you have a validated classification, routing is just a lookup table. Never let an LLM decide where to send things.

3. **The LLM should do ONE thing.** In this case: classify. Not parse, not route, not summarize. One job, structured output, validated result.

4. **Hallucination detection is a D problem.** Compare input IDs to output IDs. If the LLM invented items or dropped items, the validation step catches it instantly.

5. **Telemetry changes everything.** Once you can see that Step 2 fails 8% of the time on items with URLs, you can fix the prompt specifically for that case.
