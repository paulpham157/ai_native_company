# Mode Selection Rubric — Quick vs Deep

> Rubric quyết định chọn Quick mode hay Deep mode khi tạo SOP. Dựa trên complexity, cross-department count, risk level, và domain expertise cần thiết.

## Selection Matrix

| Criteria | Quick Mode | Deep Mode |
|----------|-----------|-----------|
| Complexity | Simple (1-3 steps) | Complex (4+ steps, nhiều decision points) |
| Cross-department | Low (0-1 dept) | High (2+ departments) |
| Risk level | Low — medium | Medium — high |
| Domain expertise | Minimal (team tự biết) | Significant (cần research) |
| SOP type | `documentation-only` | `operational` |
| Regulatory impact | None | Compliance/legal involved |
| Frequency | Daily/weekly routine | Monthly/quarterly/one-time |

## Scoring Guide

Tính tổng điểm để quyết định:

| Factor | Weight | Score 1 | Score 3 | Score 5 |
|--------|--------|---------|---------|---------|
| Complexity | 3 | 1-3 bước | 4-6 bước | 7+ bước |
| Departments | 2 | 1 dept | 2 dept | 3+ dept |
| Risk | 2 | Low | Medium | High |
| Regulatory | 3 | None | Basic | Strict |

**Threshold:** Tổng weighted score >= 20 → Deep mode. Dưới 20 → Quick mode.

## Mode Decision Output

Khi chọn mode, emit `deep-analysis-trigger` artifact theo schema:

```json
{
  "needs_deep_analysis": true,
  "reasoning": "SOP involves 3 departments with high compliance requirements",
  "complexity_score": 0.85,
  "cross_department_count": 3,
  "risk_level": "high",
  "evidence": [
    {"claim": "Cross-department workflow detected", "source": "department charter"}
  ],
  "confidence_score": 0.8,
  "need_review": false
}
```

## User Override

Luôn cho phép user chọn mode bất kể rubric recommendation. Ghi nhận lý do override vào `evidence`:

```json
{
  "claim": "User override: Deep mode despite Quick recommendation",
  "verbatim_quote": "Tôi muốn phân tích sâu dù SOP đơn giản",
  "source": "user conversation"
}
```
