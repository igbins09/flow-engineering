# Skill: {{SKILL_NAME}}

## Description
{{One-line description of what this skill does.}}

## Trigger
Use when {{describe the trigger condition — what the user says or what event fires}}.

---

## Flow (D-P-D Chain)

```
Step 1 [D] → Fetch input data
Step 2 [P] → LLM classifies / generates / decides
Step 3 [D] → Validate LLM output against schema
Step 4 [P] → LLM refines (if validation passed, optional)
Step 5 [D] → Execute action + log telemetry
```

### Step 1: Fetch Input [D]
Run `scripts/fetch.py` to gather all required input data.

**Input:** {{describe expected input — file path, API endpoint, user message, etc.}}
**Output:** Structured JSON:
```json
{
  "items": [],
  "metadata": {
    "source": "",
    "timestamp": "",
    "count": 0
  }
}
```

### Step 2: LLM Decision [P]
Given the fetched data, {{describe what the LLM should decide/generate/classify}}.

**Prompt context:**
- {{Context item 1}}
- {{Context item 2}}
- {{Any rules, constraints, or examples}}

**Required output format (structured JSON):**
```json
{
  "decision": "",
  "confidence": 0.0,
  "reasoning": "",
  "items": [
    {
      "id": "",
      "classification": "",
      "action": ""
    }
  ]
}
```

> IMPORTANT: Output MUST be valid JSON. No markdown wrapping. No prose before or after.

### Step 3: Validate Output [D]
Run `scripts/validate.py` on the LLM output.

**Validation checks:**
- [ ] Valid JSON (parseable)
- [ ] All required fields present
- [ ] `classification` values are in allowed enum: `[{{list valid values}}]`
- [ ] `confidence` is a float between 0.0 and 1.0
- [ ] No empty `items` array (at least 1 result)

**On failure:** Log the validation error and {{retry / escalate / abort}}.

### Step 4: LLM Refinement [P] (Optional)
If Step 3 passed but results need refinement:
- {{Describe refinement criteria}}
- {{e.g., "Merge duplicate classifications", "Add missing context"}}

### Step 5: Execute [D]
Run `scripts/execute.py` with the validated output.

**Actions:**
- {{Action 1 — e.g., write to database}}
- {{Action 2 — e.g., send notification}}
- {{Action 3 — e.g., move files}}

---

## Structured Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["decision", "confidence", "items"],
  "properties": {
    "decision": {
      "type": "string",
      "enum": ["{{value1}}", "{{value2}}", "{{value3}}"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "reasoning": {
      "type": "string"
    },
    "items": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "classification", "action"],
        "properties": {
          "id": { "type": "string" },
          "classification": { "type": "string" },
          "action": { "type": "string" }
        }
      }
    }
  }
}
```

---

## Telemetry

Log every run to the `workflow_runs` and `step_runs` tables.

**Tracked metrics:**
- Total duration (ms)
- Per-step duration (ms)
- Success / failure per step
- Input/output hash (for regression detection)
- Validation failure reasons

**Circuit breaker:**
If this skill fails {{N}} times consecutively:
1. Log the failure pattern
2. Alert via {{notification channel}}
3. Pause automatic execution until manually reviewed

**Thresholds:**
- Max consecutive failures before circuit break: {{3}}
- Min confidence to proceed: {{0.8}}
- Max retry attempts per P step: {{2}}

---

## Gotchas
- {{Known edge case 1}}
- {{Known edge case 2}}
- {{Common failure mode and how to handle it}}
