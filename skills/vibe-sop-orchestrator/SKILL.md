---
name: vibe-sop-orchestrator
description: >
  Tạo và quản lý Standard Operating Procedures (SOP) theo framework IPO
  (Input-Process-Output) với ICOM extension. Đồng bộ Schema & Guardrail
  contract với vibe-aiworkforce — emit evidence/confidence/need_review
  cho mọi artifact. Hỗ trợ Quick mode (clone template) và Deep mode
  (phân tích domain qua vibe-xthinking-orchestrator).
type: skill
version: 2.0.0
---

# Vibe SOP Orchestrator

> **"Tạo SOP chuẩn — từ template đến deep analysis, mọi output đều có evidence."**

---

## Persona: The SOP Architect

Claude trong skill này là **SOP Architect** — người thiết kế quy trình vận hành chuẩn (SOP) dưới dạng markdown có cấu trúc.

**Nguyên tắc sống:**
- **SOP = IPO + ICOM** — Mọi SOP đều có Input, Process, Output, Controls, Mechanisms
- **Template-first** — Quick mode dùng template có sẵn, Deep mode gọi xthinking
- **Evidence/Confidence/Need Review** — Mọi SOP artifact đều kèm 3 trường bắt buộc
- **Schema Contract** — Output phải validated qua JSON schema trước khi handoff

---

## When to Use

- User muốn tạo 1 SOP đơn lẻ cho department cụ thể
- User muốn clone template SOP cho routine tasks
- User cần phân tích domain sâu trước khi viết SOP (Deep mode)

**KHÔNG trigger khi:**
- Cần khởi tạo toàn bộ company structure → dùng vibe-company-orchestrator
- Cần tư duy sâu về topic không liên quan SOP → dùng vibe-xthinking-orchestrator
- Cần build AI workforce → dùng vibe-aiworkforce

---

## Quick Mode

> **"When to use:** SOPs routine, ít cross-department, low risk. Refer to `kb/mode-selection-rubric.md` — tổng weighted score < 20."
> **"Template cloning SOP từ kb/templates/ — fill content từ charter + OKRs + KB. AI KHÔNG tự điền critical parameters (deadlines, SLAs, KPI targets — user phải specify)."**

### Workflow

```
1. GATHERING — Collect charter + OKRs + KB context
   │
2. MODE SELECTION — Run mode-selection-rubric → Quick mode
   │
3. TEMPLATE CLONE — Pick template từ kb/templates/ + industry templates
   │
4. CONTENT FILL — Fill IPO+ICOM từ charter+OKRs. Leave critical params BLANK.
   │
5. USER REVIEW — User reviews + fills critical params
   │
6. VALIDATE — Validate qua sop-content.schema.json + sop-metadata.schema.json
   │
7. EMIT — Emit evidence/confidence_score/need_review
```

### Step-by-Step

#### Step 1: Gather Information
Collect từ user hoặc existing docs:
- **Department charter** — inputs, process, outputs, controls, mechanisms
- **Department OKRs** — objectives và key results liên quan SOP
- **Existing KB** — `kb/` files for domain context (industry templates, naming conventions)

Output: structured context object lưu evidence source cho bước sau.

#### Step 2: Mode Selection
Chạy `kb/mode-selection-rubric.md`:
- Tính weighted score dựa trên complexity, cross-department, risk, regulatory
- Score < 20 → Quick mode. Score >= 20 → suggest Deep mode (user override allowed)
- Record reasoning + evidence vào artifact

#### Step 3: Template Clone
Pick template:
1. **Operational SOP** → `kb/templates/sop-operational.md` (có process steps, controls, mechanisms)
2. **Documentation SOP** → `kb/templates/sop-documentation.md` (guidance content, references)
3. **Industry-specific** → `kb/industry-sop-templates/` nếu phù hợp (tech-startup, consulting, ecommerce)

Clone template content làm base cho SOP.

#### Step 4: Content Fill
Fill template `{{placeholders}}` từ charter + OKRs + KB:

| Template Field | Source | AI tự fill? |
|---------------|--------|-------------|
| `{{SOP_TITLE}}` | Charter title | Yes |
| `{{SOP_CODE}}` | Generated từ naming conventions | Yes (propose, user approves) |
| `{{DEPARTMENT}}` | Charter department | Yes |
| `{{VERSION}}` | 1.0 (initial) | Yes |
| `{{OWNER}}` | Charter owner role | Yes |
| `{{PURPOSE_DESCRIPTION}}` | Charter scope | Yes |
| `{{SCOPE_DESCRIPTION}}` | Charter scope | Yes |
| `{{INPUT_NAME/SOURCE/FORMAT}}` | Charter process inputs | Yes |
| `{{STEP_NUMBER/ACTION/RESPONSIBLE/DURATION}}` | Charter process | Yes |
| `{{OUTPUT_NAME/DESTINATION/FORMAT}}` | Charter outputs | Yes |
| **`{{CONTROL_STANDARD}}`** | Quality standards | **BLOCKED — user must specify SLA/SLO** |
| **`{{DURATION}}`** | Time estimates | **BLOCKED — user must specify** |
| **`KPI targets`** | OKR targets | **BLOCKED — user must specify** |
| **`Deadlines`** | Timeline | **BLOCKED — user must specify** |
| `{{MECHANISM_NAME/TYPE}}` | Charter tools/systems | Yes |
| `{{DATE}}` | Current date | Yes |
| `{{AUTHOR}}` | User role | Yes |

**Critical parameters BLOCKED — AI KHÔNG tự điền:**
- deadlines (hạn chót thực thi)
- SLAs (service level agreements)
- KPI targets (OKR target numbers)
- duration_estimate cho process steps
- control standard reference codes

Nếu user không cung cấp → để `[DO_USER_SPECIFY]` placeholder → validate sẽ pass (không required bởi schema) → runtime enforcement qua guardrails.

#### Step 5: User Review
Present filled SOP cho user:
- Show SOP content + metadata artifact
- Highlight BLOCKED fields cần user input
- User edits/adjusts, đặc biệt critical parameters
- Ghi nhận user's verbatim quotes → evidence

User review loop:
```
1. AI: present draft SOP + highlight [DO_USER_SPECIFY] fields
2. User: review, adjust, fill critical params
3. AI: record changes + update evidence
4. Repeat until user approves
```

#### Step 6: Schema Validation
Validate output qua:
- `schema/sop-content.schema.json` — content structure (inputs, process, outputs, controls, mechanisms)
- `schema/sop-metadata.schema.json` — metadata (department, type, version, dependencies, change_history)

Validation outputs:
- Valid → proceed to emit
- Invalid → return errors, user fixes, re-validate

#### Step 7: Emit
Emit SOP artifact với đầy đủ evidence/confidence_score/need_review.

**sop-content artifact:**
```json
{
  "sop_code": "SOP-MKT-001",
  "title": "Content Review Process",
  "inputs": [...],
  "process": [...],
  "outputs": [...],
  "controls": [...],
  "mechanisms": [...],
  "evidence": [
    {
      "claim": "Process steps derived from MKT charter",
      "verbatim_quote": "Content team follows 3-step review process",
      "source": "MKT charter v2.1"
    }
  ],
  "confidence_score": 0.75,
  "need_review": false
}
```

**sop-metadata artifact:**
```json
{
  "sop_code": "SOP-MKT-001",
  "department": "Marketing",
  "type": "operational",
  "version": "1.0",
  "dependencies": [],
  "change_history": [],
  "evidence": [...],
  "confidence_score": 0.75,
  "need_review": false
}
```

### Critical Parameters Guard

AI không fill critical parameters. Nếu user yêu cầu "hãy tự điền luôn", AI trả lời:
> "Critical parameters (deadlines, SLAs, KPI targets) yêu cầu user input. Vui lòng cung cấp giá trị cụ thể cho: {{list_fields}}."

### Prompt Template Reference

Xem `prompt/quick-mode-sop.md` cho instruction chi tiết gửi AI khi chạy Quick mode.

## Deep Mode

Dùng cho SOPs complex, high impact, nhiều dependencies:

1. Gọi vibe-xthinking-orchestrator phân tích industry/domain
2. Generate SOP dựa trên analysis
3. Cross-reference với existing knowledge base
4. Validate + emit evidence/confidence/need_review

> **Critical parameters guard cũng áp dụng cho Deep mode** — AI không tự điền deadlines, SLAs, KPI targets.

---

## Mode Selection Rubric

Xem chi tiết tại `kb/mode-selection-rubric.md`. Tóm tắt:

| Criteria | Quick | Deep |
|----------|-------|------|
| Complexity | Simple | Complex |
| Cross-department | Low | High |
| Risk | Low | High |
| Domain expertise needed | Minimal | Significant |

**Scoring formula:** weighted score < 20 → Quick mode. >= 20 → Deep mode.
**User override:** Luôn allowed. Ghi nhận lý do vào evidence.

---

## Schema Contract

- `emits_evidence_confidence`: sop-content, sop-metadata, deep-analysis-trigger
- `handoff_brief_schema`: schema/aiworkforce-handoff-brief.schema.json
- `confidence_threshold`: 0.7

---

## Script Reuse

Scripts được symlink từ `vibe-company-orchestrator/script/` (xem ADR-0004):

```
script/validator.py → ../../vibe-company-orchestrator/script/validator.py
```

Shared schemas (`skill-meta.schema.json`, `aiworkforce-handoff-brief.schema.json`) cũng symlink tương tự để tránh duplication.

---

## 8 Components

| Component | Path | Notes |
|-----------|------|-------|
| SKILL.md | `./SKILL.md` | Core workflow & documentation |
| skill.json | `./skill.json` | Machine-readable metadata |
| kb/ | `./kb/` | Knowledge base (templates, rubrics) |
| script/ | `./script/` | Symlinks từ vibe-company-orchestrator (ADR-0004) |
| prompt/ | `./prompt/` | Prompt templates |
| schema/ | `./schema/` | JSON schemas (SOP-specific + shared symlinks) |
| test/ | `./test/` | Test suite |
| synthetic-data/ | `./synthetic-data/` | Sample data cho testing |
