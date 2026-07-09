# Evidence Rubric — vibe-xthinking-orchestrator

> **Rubric đánh giá chất lượng evidence cho mọi analysis output.**

## Evidence Levels

| Level | Label | Description | Example |
|-------|-------|-------------|---------|
| 1 | Unsupported | No source, just opinion | "Cloud is better" |
| 2 | Anecdotal | Personal experience, 1 source | "We saw 30% improvement" |
| 3 | Referenced | Cited external source | "Per Gartner 2025 report" |
| 4 | Verified | Multiple sources, cross-validated | "3 independent analysts agree" |
| 5 | Measured | Quantitative data with methodology | "Survey n=500, ±4% margin" |

## Confidence Score Mapping

| Evidence Level | Max Confidence |
|----------------|----------------|
| 1 (Unsupported) | 0.3 |
| 2 (Anecdotal) | 0.5 |
| 3 (Referenced) | 0.7 |
| 4 (Verified) | 0.85 |
| 5 (Measured) | 0.95 |

## Evidence Structure

Mỗi evidence entry cần:
- `claim` — What is being asserted
- `source` — Where the claim comes from
- `confidence` — Agent's confidence in this evidence (0-1)

## Validation Criteria

- Evidence phải cụ thể, measurable nếu có thể
- Source phải traceable (report name, URL, document reference)
- Claims không được contradict nhau
- Conflicting evidence phải được ghi nhận (không ignored)
