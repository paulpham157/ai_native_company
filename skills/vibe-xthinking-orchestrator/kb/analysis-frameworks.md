# Analysis Frameworks — vibe-xthinking-orchestrator

> **Frameworks cho MODE PROBLEM và MODE DECISION.**

---

## 5 Whys (MODE PROBLEM)

**Khi dùng:** Problems đơn giản, single root cause, causal chain rõ ràng.

### Format
```
Problem: [statement]

Why 1: [immediate cause]
  → Evidence: [source]

Why 2: [cause of Why 1]
  → Evidence: [source]

...

Why 5 (Root Cause): [fundamental cause]
  → Evidence: [source]

Corrective Actions:
1. [action 1]
2. [action 2]
```

### Example
```
Problem: Customer churn rate tăng 15% trong Q2

Why 1: Customers không renew subscription sau trial
  → Evidence: Subscription analytics

Why 2: Customers không thấy value trong 30 ngày đầu
  → Evidence: User onboarding funnel data

Why 3: Onboarding process không có structured guidance
  → Evidence: UX review, support tickets

Why 4: Product team tập trung vào features, không phải time-to-value
  → Evidence: Sprint retrospective notes

Why 5 (Root Cause): Không có onboarding OKR hoặc metric theo dõi time-to-value
  → Evidence: OKR document, product roadmap

Actions:
1. Thiết lập onboarding OKR với time-to-value metric
2. Implement structured onboarding với milestones
```

---

## Fishbone (Ishikawa) — MODE PROBLEM

**Khi dùng:** Problems phức tạp, multiple categories, cần brainstorm systematic.

### Categories
- **People** — Skills, knowledge, staffing, communication
- **Process** — Workflow, procedures, methods, policies
- **Technology** — Tools, systems, infrastructure, automation
- **Materials** — Inputs, data, resources, supplies
- **Measurement** — Metrics, KPIs, monitoring, reporting
- **Environment** — Culture, regulations, market, facilities

### Format
```
Problem: [statement]

People:
  - [cause 1] (evidence)
  - [cause 2] (evidence)

Process:
  - [cause 1] (evidence)

Technology:
  - [cause 1] (evidence)

Materials:
  - [cause 1] (evidence)

Measurement:
  - [cause 1] (evidence)

Environment:
  - [cause 1] (evidence)

Root Causes (prioritized):
1. [cause] — [category] — [evidence strength]
```

---

## Eisenhower Matrix (MODE DECISION)

**Khi dùng:** Prioritization problems, resource allocation, time management.

### Matrix

| | Urgent | Not Urgent |
|---|--------|------------|
| **Important** | DO FIRST (Quadrant 1) | SCHEDULE (Quadrant 2) |
| **Not Important** | DELEGATE (Quadrant 3) | ELIMINATE (Quadrant 4) |

### Scoring
- Mỗi option được đánh giá urgency (1-5) và importance (1-5)
- Q1: urgency >= 3 && importance >= 3 → Do First
- Q2: urgency < 3 && importance >= 3 → Schedule
- Q3: urgency >= 3 && importance < 3 → Delegate
- Q4: urgency < 3 && importance < 3 → Eliminate

---

## RICE (MODE DECISION)

**Khi dùng:** Product decisions, feature prioritization, project selection.

### Dimensions
| Dimension | Scale | Description |
|-----------|-------|-------------|
| Reach | 1-10 | How many users/customers affected per quarter |
| Impact | 1-10 | How much impact per user (massive=3x, high=2x, medium=1x, low=0.5x) |
| Confidence | 1-10 | How confident in estimates (high=100%, medium=80%, low=50%) |
| Effort | months | Total engineering effort (person-months) |

### Formula
```
RICE Score = (Reach × Impact × Confidence) / Effort
```

### Example
| Option | Reach | Impact | Confidence | Effort | Score |
|--------|-------|--------|------------|--------|-------|
| Feature A | 8 | 3 | 8 | 2 | 96 |
| Feature B | 5 | 2 | 9 | 3 | 30 |
| Feature C | 9 | 1 | 7 | 1 | 63 |

---

## Decision Matrix (MODE DECISION)

**Khi dùng:** Complex decisions với multiple weighted criteria.

### Format
```
Decision: [question]

Criteria:
  C1: [name] — weight: [0-1]
  C2: [name] — weight: [0-1]
  ...

Options:
  Option A:
    C1: score [1-10] × weight = [weighted]
    C2: score [1-10] × weight = [weighted]
    Total: [sum]

  Option B:
    C1: score [1-10] × weight = [weighted]
    C2: score [1-10] × weight = [weighted]
    Total: [sum]

Recommendation: [option with highest total]
Sensitivity: [what if weights change?]
```
