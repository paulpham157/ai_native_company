# Quality Standards — SLI/SLO/SLA cho SOP Operations

> Reference cho việc define quality standards liên quan đến SOP execution. Áp dụng cho `controls[].standard` trong sop-content schema.

## Quick Rules

1. **Mỗi control phải có standard reference** — KHÔNG "chất lượng cao", "đúng quy định"
2. **SLO KHÔNG target 100%** — cần error budget cho exception handling
3. **SLA less strict hơn SLO** — tạo buffer cho external commitments
4. **Mỗi control standard phải traceable** — link/file reference cụ thể

## Standard Reference Format

```
{Type}-{Department}-{NNN}
```

| Type | Ý nghĩa |
|------|---------|
| QC | Quality Control |
| POL | Policy |
| STD | Standard |
| REG | Regulation |

## SLI Examples theo Department

| Department | SLI Examples |
|-----------|-------------|
| Marketing | Factual accuracy rate, on-time delivery rate, brand compliance rate |
| Engineering | Code review turnaround, deploy success rate, bug reintroduction rate |
| HR | Hiring timeline compliance, document completion rate |
| Finance | Reconciliation accuracy, report on-time rate |
| Operations | Order accuracy, fulfillment SLA compliance |

## SOP Quality Gates

| Gate | Description | Standard |
|------|-------------|----------|
| Input validation | Input đủ và đúng format | QC-001 |
| Process compliance | Các step được follow đúng sequence | QC-002 |
| Output verification | Output đạt quality bar trước khi handoff | QC-003 |
| Control adherence | Controls được áp dụng đầy đủ | QC-004 |

## Evidence cho Quality Standards

Khi SOP references một quality standard:

```json
{
  "claim": "Content must pass QC-001 before publishing",
  "verbatim_quote": "Bài viết phải đạt QC-001 trước khi xuất bản",
  "source": "MKT charter v2.1",
  "location": "line 78"
}
```

→ Xem `evidence-rubric.md` cho confidence scoring chi tiết.
