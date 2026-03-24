<p align="center">
  <img src="diagrams/flow-engineering-banner.png" alt="Flow Engineering" width="600">
</p>

<h1 align="center">Flow Engineering</h1>

<p align="center">
  <strong>Stop vibing. Start engineering.</strong>
</p>

<p align="center">
  A framework for building reliable AI agent systems using deterministic validation gates.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://github.com/igbins09/flow-engineering/stargazers"><img src="https://img.shields.io/github/stars/igbins09/flow-engineering?style=social" alt="Stars"></a>
  <a href="https://richardigbinoba.com"><img src="https://img.shields.io/badge/site-richardigbinoba.com-black" alt="Website"></a>
</p>

---

## The Problem

Large language models are probabilistic. Every time you ask one to make a decision, there's a margin of error. Chain five decisions together and the math gets brutal:

| Steps | Success Rate (90% per step) |
|-------|---------------------------|
| 1     | 90.0%                     |
| 2     | 81.0%                     |
| 3     | 72.9%                     |
| 4     | 65.6%                     |
| 5     | 59.0%                     |
| 6     | 53.1%                     |
| 7     | 47.8%                     |
| 8     | 43.0%                     |
| 9     | 38.7%                     |
| 10    | 34.9%                     |

**90% accuracy per step. 5 steps. 59% end-to-end success.**

This isn't theoretical. The research confirms it:

- **WebArena** (Zhou et al., 2023): Best agents achieved **14.4% task success** on real web tasks. Humans hit 78.2%.
- **TheAgentCompany** (2024): Best agent scored **24%** on real-world professional tasks.
- **Dziri et al., NeurIPS 2023**: Compositional reasoning degrades multiplicatively with each chained step.
- **Wei et al., 2023**: Arithmetic accuracy drops from 95% (2-digit) to 60% (5-digit) as problem complexity scales.

**If you're chaining LLM calls without validation, you're building a 59% system.**

---

## The Solution: D-P-D

**Deterministic - Probabilistic - Deterministic.**

The core principle: never let two probabilistic (LLM) steps run back-to-back without a deterministic validation gate between them.

```
LLM proposes.  Code proves.  Code acts.  Code checks.
```

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│      D      │────>│        P        │────>│      D      │
│  Fetch data │     │  LLM classifies │     │  Validate   │
│  Parse input│     │  LLM generates  │     │  Type-check │
│  Retrieve   │     │  LLM decides    │     │  Assert     │
└─────────────┘     └─────────────────┘     └─────────────┘
       │                                           │
       │            ┌─────────────────┐            │
       │            │        P        │            │
       │            │  LLM refines    │<───────────┘
       │            │  (if needed)    │
       │            └────────┬────────┘
       │                     │
       │            ┌─────────────────┐
       └───────────>│      D          │
                    │  Execute action │
                    │  Log telemetry  │
                    │  Return result  │
                    └─────────────────┘
```

### The Rules

1. **Map every step as D or P.** If it uses an LLM, it's P. Everything else is D.
2. **If P-P exists, insert a D validation step.** No exceptions.
3. **Every P step returns structured JSON.** Not prose. Not markdown. JSON with a schema.
4. **Every D step validates before proceeding.** Type checks, range checks, required fields.
5. **Log every step to telemetry.** You can't improve what you don't measure.

---

## Quick Start (5 Minutes)

### Step 1: Audit your current workflow

List every step in your AI workflow. Label each one:

- **D** = Deterministic (code, API call, database query, file read)
- **P** = Probabilistic (LLM call, generation, classification)

### Step 2: Find P-P chains

Look for any place where one LLM call feeds directly into another. These are your failure points.

### Step 3: Insert validation gates

Between every P-P pair, add a D step that validates the output:

```python
# Before: P -> P (59% chain)
classification = llm_classify(input_text)      # P
action_plan = llm_plan(classification)          # P  <-- operating on unvalidated output

# After: D -> P -> D -> P -> D (reliable chain)
raw_input = parse_input(input_text)             # D: structured parsing
classification = llm_classify(raw_input)        # P: LLM decision
validated = validate_classification(classification)  # D: schema + enum check
action_plan = llm_plan(validated)               # P: LLM planning
execute_plan(action_plan)                       # D: deterministic execution
```

### Step 4: Structure all LLM outputs

Every P step must return JSON with a defined schema:

```json
{
  "classification": "high_priority",
  "confidence": 0.92,
  "reasoning": "Contains deadline keyword and urgent tone",
  "suggested_action": "route_to_immediate_queue"
}
```

### Step 5: Add telemetry

Log every step so you can measure and improve:

```sql
INSERT INTO step_runs (workflow_run_id, step_name, step_type, input_hash, output_hash, duration_ms, success)
VALUES (?, ?, 'P', ?, ?, ?, ?);
```

See [`templates/telemetry.sql`](templates/telemetry.sql) for the full schema.

---

## Architecture

Every AI skill follows the same structure:

```
skill-name/
├── SKILL.md              <- P layer (LLM decisions, prompts, context)
└── scripts/
    ├── fetch.py           <- D layer (data retrieval, API calls)
    ├── validate.py        <- D layer (output validation, assertions)
    └── execute.py         <- D layer (side effects, writes, notifications)
```

**The SKILL.md is the only probabilistic layer.** Everything in `scripts/` is deterministic, testable, and debuggable.

This means:
- When the LLM hallucinates, `validate.py` catches it
- When an API changes, you fix `fetch.py` — not a prompt
- When you need to audit, `execute.py` has the full log
- When accuracy drops, telemetry tells you which P step degraded

---

## Validation Strategies

Ranked by ROI. Start at Tier 1. Add Tier 2 for high-stakes workflows. Tier 3 when you're optimizing.

### Tier 1: Always Do These

| Strategy | What It Does | Example |
|----------|-------------|---------|
| **JSON schema validation** | Verify LLM output matches expected structure | `jsonschema.validate(output, schema)` |
| **Required field checks** | Reject outputs missing critical fields | `assert all(k in output for k in required_keys)` |
| **Enum/range validation** | Constrain values to valid options | `assert output["priority"] in ["low", "medium", "high"]` |
| **Type checking** | Ensure correct data types | `assert isinstance(output["score"], (int, float))` |

### Tier 2: High-Stakes Workflows

| Strategy | What It Does | Example |
|----------|-------------|---------|
| **Cross-model validation** | Run same prompt through 2+ models, compare | GPT + Claude + Gemini majority vote |
| **Confidence thresholds** | Reject low-confidence outputs | `if output["confidence"] < 0.8: escalate()` |
| **Semantic similarity check** | Verify output relates to input | Embedding cosine similarity > 0.7 |
| **Idempotency guards** | Prevent duplicate side effects | Check `execution_log` before writing |

### Tier 3: Optimization

| Strategy | What It Does | Example |
|----------|-------------|---------|
| **A/B prompt testing** | Compare prompt variants on same inputs | Log variant + success rate per step |
| **Regression testing** | Golden dataset of input/expected output pairs | `pytest test_golden.py` |
| **Cost-per-success tracking** | Measure $/successful completion | `cost / success_count` per workflow |
| **Drift detection** | Alert when accuracy drops below baseline | Weekly telemetry review |

---

## Real Results

We refactored 23 AI skills from prose-only LLM chains to D-P-D architecture:

- **P steps dropped from 60 to 25** — pushed 58% of logic into deterministic code
- **Every skill now has deterministic validation gates** — no unvalidated P-P chains remain
- **Structured JSON output on all LLM calls** — no more parsing prose with regex
- **Full telemetry** — every step logged with duration, success/failure, and input/output hashes
- **Debugging time cut by 70%** — when something fails, telemetry points to the exact step

The 90/59 principle isn't just math. It's the entire design philosophy: **push complexity into deterministic code so your probabilistic steps do as little as possible.**

---

## What's Included

### `/templates`
- **[`skill-creator/`](templates/skill-creator/)** — Full skill scaffolding template with D-P-D flow, structured output, and telemetry
- **[`scripts/`](templates/scripts/)** — Generic `fetch.py`, `validate.py`, `execute.py` templates
- **[`telemetry.sql`](templates/telemetry.sql)** — SQLite schema for workflow tracking (3 tables)

### `/examples`
- **[`before-after.md`](examples/before-after.md)** — Real before/after of a triage skill refactored from 4 chained P steps to D-P-D

### `/research`
- **[`citations.md`](research/citations.md)** — Academic papers backing the 90/59 principle
- **[`cross-validation-prompt.md`](research/cross-validation-prompt.md)** — Prompt for cross-validating ideas across multiple LLMs

### `/diagrams`
- **[`flow-engineering-chain.d2`](diagrams/flow-engineering-chain.d2)** — D2 source for the D-P-D chain diagram

---

## The Philosophy

Most AI agent frameworks focus on orchestration — how to chain LLM calls together. Flow Engineering focuses on **what goes between those calls.**

The insight: reliability doesn't come from better prompts. It comes from better architecture. Specifically, from treating every LLM call as an untrusted input that must be validated before it touches anything real.

This is how traditional software engineering works. We don't trust user input. We validate it. We sanitize it. We type-check it. We log it.

LLM output is user input. Treat it that way.

---

## Links

- **Full Product:** [tools.flowthinkers.com](https://tools.flowthinkers.com)
- **YouTube:** [youtube.com/@flowthinkers](https://youtube.com/@flowthinkers)
- **LinkedIn:** [linkedin.com/in/richardigbinoba](https://linkedin.com/in/richardigbinoba)
- **X:** [@richeythinks](https://x.com/richeythinks)
- **Website:** [richardigbinoba.com](https://richardigbinoba.com)
- **Newsletter:** [richardigbinoba.substack.com](https://richardigbinoba.substack.com)

---

<p align="center">
  Built by <a href="https://richardigbinoba.com">Richard Igbinoba</a> / <a href="https://flowthinkers.com">Flowthinkers</a>
  <br>
  Flow Engineering is how I run my entire AI business.
  <br><br>
  <strong>Stop vibing. Start engineering.</strong>
</p>
