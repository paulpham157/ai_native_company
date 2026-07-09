# Evidence Tracking Rubric — vibe-xthinking-orchestrator

> **Rubric cho evidence tracking và aggregation trong multi-agent MODE TOPIC.**

## Per-Agent Evidence Quality

| Criterion | 1 (Weak) | 2 (Moderate) | 3 (Strong) |
|-----------|----------|---------------|-------------|
| Source quality | Unclear source | Referenced source | Verified source |
| Claim specificity | Vague | Specific | Measurable |
| Reasoning | Assertion only | Basic logic | Chain of reasoning |
| Cross-reference | No cross-ref | 1 other agent | 2+ other agents |

## Evidence Chain Aggregation

```
Aggregate Confidence = weighted_average(
    Researcher.confidence × w1,
    ExplicitThinker.confidence × w2,
    ValueChainAnalyst.confidence × w3,
    Synthesizer.confidence × w4,
    Validator.confidence × w5
)
```

Default weights: w1=0.15, w2=0.2, w3=0.2, w4=0.2, w5=0.25

## Conflict Resolution

Khi agents disagree:
1. Record both perspectives trong evidence chain
2. Validator decides based on evidence strength
3. Mark conflicting items với `need_review: true`
4. Giảm aggregate confidence tương ứng
