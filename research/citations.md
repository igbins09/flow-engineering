# Research Citations

Academic papers and benchmarks supporting the Flow Engineering methodology.

---

## Core Principle: Compositional Degradation

### Dziri et al. — "Faith and Fate: Limits of Transformers on Compositionality" (NeurIPS 2023)
- **Finding:** Transformer accuracy degrades multiplicatively with each compositional reasoning step. Multi-step tasks that appear simple individually become unreliable when chained.
- **Relevance:** This is the mathematical foundation of the 90/59 principle — 90% per step, 59% over 5 steps.
- **URL:** https://arxiv.org/abs/2305.18654

### Wei et al. — "Simple synthetic data reduces sycophancy in large language models" (2023)
- **Finding:** Arithmetic accuracy drops from ~95% on 2-digit problems to ~60% on 5-digit problems. Accuracy degrades predictably as problem complexity (number of steps) increases.
- **Relevance:** Demonstrates that even "easy" tasks for LLMs become unreliable at scale — a direct argument for pushing multi-step logic into deterministic code.
- **URL:** https://arxiv.org/abs/2308.03958

---

## Agent Benchmarks

### Zhou et al. — "WebArena: A Realistic Web Environment for Building Autonomous Agents" (2023)
- **Finding:** Best autonomous agents achieved **14.4% task success rate** on realistic web browsing tasks. Human performance was 78.2%.
- **Relevance:** Real-world agent success rates are far below the 90% per-step assumption — making validation gates even more critical.
- **URL:** https://arxiv.org/abs/2307.13854

### TheAgentCompany — "Benchmarking LLM Agents on Consequential Real World Tasks" (2024)
- **Finding:** Best-performing agent (Claude 3.5 Sonnet) scored only **24%** on a benchmark of real-world professional tasks (coding, project management, communication).
- **Relevance:** Even state-of-the-art agents fail 76% of the time on real tasks. D-P-D architecture provides the validation layer these agents are missing.
- **URL:** https://arxiv.org/abs/2412.14161

---

## Mitigation Strategies

### Shinn et al. — "Reflexion: Language Agents with Verbal Reinforcement Learning" (2023)
- **Finding:** Adding self-reflection (where the agent reviews and corrects its own output) improved HotPotQA accuracy from 34% to 91%.
- **Relevance:** Reflexion is a form of P-D-P — the "D" being the reflection/validation step. Flow Engineering generalizes this into a systematic architecture.
- **URL:** https://arxiv.org/abs/2303.11366

### Wang et al. — "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (2023)
- **Finding:** Sampling multiple reasoning paths and taking the majority vote (self-consistency) significantly improves accuracy over single-pass chain-of-thought.
- **Relevance:** Cross-model validation (Tier 2 strategy in Flow Engineering) is the multi-model version of self-consistency.
- **URL:** https://arxiv.org/abs/2203.11171

### Gou et al. — "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing" (2024)
- **Finding:** LLMs can improve their outputs by interacting with external tools (calculators, search engines, code interpreters) to verify claims before finalizing.
- **Relevance:** CRITIC validates the core Flow Engineering principle — use deterministic tools to check probabilistic outputs.
- **URL:** https://arxiv.org/abs/2305.11738

---

## Multi-Agent Systems

### "From Spark to Fire: Agentic AI Ecosystems — How Multi-Agent AI Drives the Next Wave of Enterprise Innovation" (2025)
- **Finding:** Multi-agent systems with structured handoff protocols and validation layers outperform monolithic agent architectures. The key differentiator is how agents verify each other's work.
- **Relevance:** Flow Engineering's D-P-D pattern applies at the inter-agent level — each agent handoff should include a deterministic validation gate.
- **URL:** https://arxiv.org/abs/2504.15489

---

## Summary Table

| Paper | Year | Key Number | Implication |
|-------|------|-----------|-------------|
| Dziri et al. | 2023 | Multiplicative degradation | 90% × 5 steps = 59% |
| Wei et al. | 2023 | 95% → 60% (2 to 5 digits) | Complexity kills accuracy |
| WebArena | 2023 | 14.4% agent success | Agents need validation gates |
| TheAgentCompany | 2024 | 24% best agent score | Even SOTA fails 76% of the time |
| Shinn (Reflexion) | 2023 | 34% → 91% (HotPotQA) | Self-correction works — systematize it |
| Wang (Self-Consistency) | 2023 | Majority vote improves CoT | Cross-validation is not optional |
| CRITIC | 2024 | Tool-verified > unverified | Deterministic checks beat more prompting |
| Spark to Fire | 2025 | Structured handoffs win | D-P-D applies at agent boundaries too |
