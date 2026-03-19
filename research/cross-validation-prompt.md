# Cross-Validation Prompt

Use this prompt to validate architectural decisions across multiple LLMs. Run the same prompt through 2-3 different models (e.g., GPT, Claude, Gemini, Grok) and compare responses.

The goal is **convergence testing** — if 3 independent models arrive at the same conclusion from different training data, confidence in the conclusion is significantly higher than any single model's output.

---

## The Prompt

```
I'm designing an architecture pattern for AI agent systems. I need you to evaluate this claim and provide counter-arguments if you disagree.

**Claim:** In multi-step AI workflows, chaining LLM calls without deterministic validation between them produces unreliable systems. Specifically:

1. Each LLM step has ~90% accuracy (optimistic estimate)
2. Chaining 5 steps: 0.9^5 = 59% end-to-end success
3. The fix: insert deterministic validation (schema checks, type checks, enum validation) between every pair of LLM steps

**The pattern is called D-P-D (Deterministic-Probabilistic-Deterministic):**
- D steps: code that fetches data, validates output, executes actions
- P steps: LLM calls that classify, generate, or decide
- Rule: never chain P→P without a D validation gate between them

**My questions:**
1. Is the 90% per-step accuracy estimate reasonable? What does the literature suggest?
2. Is multiplicative degradation the correct model for chained LLM steps, or is it more nuanced?
3. What are the strongest counter-arguments to this architecture?
4. Are there scenarios where P→P chaining is actually preferable?
5. What validation strategies have the highest ROI for the least implementation effort?

Please be specific and cite research where possible. I want genuine critique, not agreement.
```

---

## How to Use

### Step 1: Run Across Models
Send the exact same prompt to at least 3 different LLMs:
- GPT-4 / GPT-4o
- Claude (Sonnet or Opus)
- Gemini Pro / Flash
- Grok
- DeepSeek

### Step 2: Compare Responses
Look for:
- **Convergence:** Points where all models agree (high confidence)
- **Divergence:** Points where models disagree (investigate further)
- **Novel arguments:** Unique insights from individual models
- **Citation quality:** Which models provide verifiable references

### Step 3: Synthesize
Create a summary with:
- Consensus findings (all models agree)
- Contested claims (models disagree — note the split)
- New considerations (raised by only one model but compelling)
- Action items (what to change based on the findings)

---

## Expected Findings

Based on previous cross-validation runs, models typically converge on:

1. **90% is optimistic.** Real-world accuracy per step is often 70-85% depending on task complexity, making the case for D-P-D even stronger.

2. **Multiplicative degradation is correct** for independent steps but can be mitigated by error-correcting intermediate steps — which is exactly what D validation gates provide.

3. **The strongest counter-argument** is overhead: adding validation gates increases development time and latency. The rebuttal is that debugging time saved far exceeds development time added.

4. **P-P is acceptable** only when both steps operate on the same context window (e.g., chain-of-thought within a single prompt) and the second P step is self-correcting (e.g., reflection).

5. **Highest-ROI validation:** JSON schema validation + required field checks. Takes 10 minutes to implement, catches 60%+ of LLM output errors.

---

## Tracking Results

Record your cross-validation results with this template:

```markdown
## Cross-Validation: [Topic]
**Date:** YYYY-MM-DD
**Models:** GPT-4o, Claude Sonnet, Gemini Flash

### Consensus
- [Point all models agreed on]

### Contested
- [Point of disagreement] — GPT says X, Claude says Y, Gemini says Z

### Novel
- [Unique insight from one model]

### Action Items
- [ ] [What to change based on findings]
```
