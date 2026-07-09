# Mode Selection Guide — vibe-xthinking-orchestrator

> **Hướng dẫn chọn MODE TOPIC vs MODE PROBLEM vs MODE DECISION.**

## Decision Tree

```
User request
  │
  ├── "Phân tích [topic/industry/domain]"
  │   └── → MODE TOPIC (multi-agent)
  │
  ├── "Tại sao [problem]?" / "Root cause của [issue]"
  │   └── → MODE PROBLEM (single-agent)
  │
  ├── "Nên chọn [option A] hay [option B]?"
  │   └── → MODE DECISION (single-agent)
  │
  └── Handoff từ vibe-sop-orchestrator
      └── → Dựa vào analysis_type field:
           ├── "topic" → MODE TOPIC
           ├── "problem" → MODE PROBLEM
           └── "decision" → MODE DECISION
```

## Criteria Table

| Criterion | MODE TOPIC | MODE PROBLEM | MODE DECISION |
|-----------|------------|--------------|---------------|
| Question type | "What/How" | "Why" | "Which" |
| Output | Comprehensive analysis | Root causes | Recommendation |
| Depth | Broad + deep | Focused deep | Comparative |
| User intervention | 2 checkpoints | 1 review | 1 review |
| Complexity | Highest | Medium | Medium-High |
| Time | Longest | Short | Medium |

## Override

User có thể override mode selection bất kỳ lúc nào:
- "Phân tích topic X nhưng dùng 5 Whys" → MODE PROBLEM với framework override
- "Quyết định A vs B, phân tích sâu" → MODE DECISION với multi-agent (override)

Ghi nhận lý do override vào evidence.
