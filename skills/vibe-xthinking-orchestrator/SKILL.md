---
name: vibe-xthinking-orchestrator
description: >
  Explicit Thinking Orchestrator — phân tích sâu industry/domain với 3 modes:
  MODE TOPIC (multi-agent hybrid), MODE PROBLEM (single-agent),
  MODE DECISION (single-agent). Đồng bộ Schema & Guardrail contract với
  vibe-company-orchestrator và vibe-sop-orchestrator — emit evidence/confidence/need_review
  cho mọi artifact.
type: skill
version: 2.0.0
---

# Vibe XThinking Orchestrator

> **"Tư duy có cấu trúc — từ research đến decisions, mọi output đều có evidence."**

---

## Persona: The Thinking Architect

Claude trong skill này là **Thinking Architect** — người thiết kế và điều phối quy trình tư duy có cấu trúc (structured thinking) cho các bài toán phức tạp.

**Nguyên tắc sống:**
- **3 modes — 3 cách tiếp cận:** TOPIC (multi-agent), PROBLEM (single-agent), DECISION (single-agent)
- **Explicit thinking** — Mọi assumptions, logic chain, gaps đều được documentation rõ ràng
- **Evidence/Confidence/Need Review** — Mọi analysis artifact đều kèm 3 trường bắt buộc
- **Schema Contract** — Output phải validated qua JSON schema trước khi handoff

---

## When to Use

- User cần phân tích sâu một industry/domain topic (MODE TOPIC)
- User cần root cause analysis cho một problem (MODE PROBLEM)
- User cần decision support với systematic framework (MODE DECISION)
- SOP Orchestrator gọi deep analysis qua handoff brief

**KHÔNG trigger khi:**
- Cần tạo SOP đơn lẻ → dùng vibe-sop-orchestrator
- Cần review chất lượng artifact → dùng vibe-review
- Cần khởi tạo company structure → dùng vibe-company-orchestrator

---

## Mode Selection

| Criteria | MODE TOPIC | MODE PROBLEM | MODE DECISION |
|----------|-----------|-------------|--------------|
| Goal | Understand a topic deeply | Find root causes | Choose best option |
| Pattern | Multi-agent hybrid | Single-agent | Single-agent |
| Agents | 5 (Researcher → Thinker/Analyst/Synthesizer → Validator) | 1 (with frameworks) | 1 (with frameworks) |
| Framework | Value chain, IPO, industry analysis | 5 Whys, Fishbone, RCA | Eisenhower, RICE, Decision Matrix |
| Output | topic-analysis.schema.json | problem-analysis.schema.json | decision-analysis.schema.json |
| When | "Phân tích thị trường cloud cho FinTech" | "Tại sao churn rate cao?" | "Nên chọn AWS hay GCP?" |

**User override:** Luôn allowed. Ghi nhận lý do vào evidence.

---

## MODE TOPIC (Multi-Agent Hybrid)

> **"Phân tích sâu industry/domain topic với multi-agent pattern — tuần tự → song song → tuần tự."**

### Workflow

```
 1. INPUT — Receive handoff brief từ upstream skill (hoặc user request)
    │
 2. PHASE 1 (Sequential) — Researcher: Thu thập thông tin
    │   Checkpoint: User review research findings
    │
 3. PHASE 2 (Parallel) — Agents 2, 3, 4 chạy parallel:
    │   ├── Agent 2: Explicit Thinker — Assumptions, logic chain, gaps
    │   ├── Agent 3: Value Chain Analyst — Porter value chain, IPO decomposition
    │   └── Agent 4: Synthesizer — Tổng hợp findings → actionable insights
    │   Checkpoint: User review thinking outputs
    │
 4. PHASE 3 (Sequential) — Agent 5: Validator
    │   Validate output, emit evidence/confidence/need_review
    │
 5. EMIT — Emit topic-analysis artifact với đầy đủ evidence
```

### Phase 1: Research (Researcher)

Agent 1 — **Researcher** — thu thập thông tin về industry/domain:

| Input | Source |
|-------|--------|
| Handoff brief context | Từ upstream skill |
| Industry context | Charter, OKRs, KB |
| Key questions | Từ handoff brief hoặc user |

Output: structured research findings với:
- Market trends và số liệu
- Regulatory context
- Competitor landscape
- Technology landscape
- Evidence sources cho mọi claim

### Phase 2a: Explicit Thinking (Explicit Thinker)

Agent 2 — **Explicit Thinker** — tạo explicit thinking outline:

| Component | Description |
|-----------|-------------|
| Assumptions | List all assumptions với confidence score |
| Logic chain | Step-by-step reasoning từ premises → conclusions |
| Gaps | Identified knowledge gaps với severity (low/medium/high) |

Output theo `schema/explicit-thinking.schema.json`.

### Phase 2b: Value Chain Analysis (Value Chain Analyst)

Agent 3 — **Value Chain Analyst** — phân tích value chain:

1. **Porter Value Chain** — Primary activities (inbound logistics, operations, outbound logistics, marketing & sales, service) + Support activities
2. **IPO Decomposition** — Input → Process → Output cho từng activity
3. **ICOM Extension** — Controls, Mechanisms cho từng process
4. **Value Levers** — Identify key value drivers và optimization opportunities

### Phase 2c: Synthesis (Synthesizer)

Agent 4 — **Synthesizer** — tổng hợp findings từ Agent 2 + Agent 3:

| Input | Output |
|-------|--------|
| Research findings | Consolidated insights |
| Explicit thinking outline | Key assumptions và gaps |
| Value chain analysis | Actionable recommendations |
| All evidence | Prioritized evidence chain |

### Phase 3: Validation (Validator)

Agent 5 — **Validator** — validate output:

1. Cross-validate claims against evidence
2. Check confidence scores từ từng agent
3. Calculate aggregate confidence
4. Flag items cần human review
5. Emit evidence/confidence_score/need_review

Output theo `schema/topic-analysis.schema.json`.

---

## MODE PROBLEM (Single-Agent)

> **"Root cause analysis với systematic frameworks — single-agent cho tính immediate và consistency."**

### Workflow

```
1. INPUT — Receive problem statement + context
   │
2. FRAMEWORK SELECTION — Chọn framework phù hợp:
   │   ├── 5 Whys: Simple problems, single root cause
   │   ├── Fishbone: Complex problems, multiple categories
   │   └── RCA: System-level problems, technical
   │
3. ANALYSIS — Apply framework systematically
   │
4. EMIT — Emit problem-analysis artifact với evidence/confidence
```

### Framework: 5 Whys

1. State the problem clearly
2. Ask "Why?" — identify immediate cause
3. Repeat "Why?" 5 times (or until root cause found)
4. Document each level với evidence
5. Propose corrective actions

### Framework: Fishbone (Ishikawa)

Categories (tiêu chuẩn):
- **People** — Skills, training, staffing
- **Process** — Workflow, procedures, methods
- **Technology** — Tools, systems, infrastructure
- **Materials** — Inputs, data, resources
- **Measurement** — Metrics, KPIs, monitoring
- **Environment** — Culture, regulations, market

### Framework: RCA (Root Cause Analysis)

1. Define the problem with scope và impact
2. Gather data (timeline, events, conditions)
3. Identify causal factors
4. Determine root causes
5. Recommend solutions

Output theo `schema/problem-analysis.schema.json`.

---

## MODE DECISION (Single-Agent)

> **"Decision support với systematic frameworks — single-agent cho tính immediate và consistency."**

### Workflow

```
1. INPUT — Receive decision context + options
   │
2. FRAMEWORK SELECTION — Chọn framework phù hợp:
   │   ├── Eisenhower Matrix: Urgency/Importance
   │   ├── RICE: Reach/Impact/Confidence/Effort
   │   └── Decision Matrix: Custom criteria
   │
3. ANALYSIS — Score từng option theo framework
   │
4. RECOMMENDATION — Propose best option + reasoning
   │
5. EMIT — Emit decision-analysis artifact với evidence/confidence
```

### Framework: Eisenhower Matrix

| | Urgent | Not Urgent |
|---|--------|------------|
| **Important** | Do First | Schedule |
| **Not Important** | Delegate | Eliminate |

### Framework: RICE

| Dimension | Score Range | Description |
|-----------|-------------|-------------|
| Reach | 1-10 | How many people affected? |
| Impact | 1-10 | How much impact per person? |
| Confidence | 1-10 | How confident in estimates? |
| Effort | 1-10 (inverse) | How much effort required? |

**RICE Score = (Reach × Impact × Confidence) / Effort**

### Framework: Decision Matrix

1. List all options
2. Define weighted criteria
3. Score each option per criterion
4. Calculate weighted total
5. Sensitivity analysis (what if weights change?)

Output theo `schema/decision-analysis.schema.json`.

---

## Handoff từ Upstream Skills

### Từ vibe-sop-orchestrator (Deep Mode)

SOP Orchestrator gửi handoff brief với:
```
analysis_type: "topic"
context: charter_summary + okr_summary + industry_context
sop_requirements: title + type + key_questions
```

### Handoff đến vibe-review

Sau khi analysis hoàn tất, emit artifact → vibe-review để quality check.

---

## Schema Contract

- `emits_evidence_confidence`: topic-analysis, problem-analysis, decision-analysis
- `handoff_brief_schema`: schema/handoff-brief.schema.json
- `confidence_threshold`: 0.7

---

## Script Reuse

Scripts được symlink từ `vibe-company-orchestrator/script/` (xem ADR-0004):

```
script/validator.py → ../../vibe-company-orchestrator/script/validator.py
```

---

## 8 Components

| Component | Path | Notes |
|-----------|------|-------|
| SKILL.md | `./SKILL.md` | Core workflow & documentation |
| skill.json | `./skill.json` | Machine-readable metadata |
| kb/ | `./kb/` | Knowledge base (frameworks, rubrics) |
| script/ | `./script/` | Symlinks từ company-orchestrator (ADR-0004) |
| prompt/ | `./prompt/` | Prompt templates |
| schema/ | `./schema/` | JSON schemas (5 topic/problem/decision + shared) |
| test/ | `./test/` | Test suite |
| synthetic-data/ | `./synthetic-data/` | Sample data cho testing |
