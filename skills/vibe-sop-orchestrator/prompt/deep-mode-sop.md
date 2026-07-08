# Deep Mode SOP — Prompt Template

> Instruction cho AI khi thực thi Deep mode workflow. Gọi vibe-xthinking-orchestrator để phân tích domain sâu trước khi generate SOP.

## Context

- Department: {{DEPARTMENT}}
- Charter: {{CHARTER_PATH}}
- OKRs: {{OKR_PATH}}
- SOP type: {{SOP_TYPE}} (operational / documentation-only)
- Industry context: {{INDUSTRY_CONTEXT}}

## Instructions

### 1. Gather Information

Read department charter + OKRs + existing KB files để hiểu domain. Trích verbatim quote cho evidence.

### 2. Mode Selection

Run mode-selection-rubric:
- Tính weighted score dựa trên complexity, cross-department, risk, regulatory
- Score >= 20 → Deep mode: tiếp tục workflow
- Score < 20 → Quick mode: suggest user chuyển Quick mode (ghi nhận override nếu user vẫn chọn Deep)
- Emit deep-analysis-trigger artifact với decision + reasoning

### 3. User Override Check

Nếu user override mode selection:
- Ghi nhận lý do override vào evidence
- Record verbatim quote của user
- Update deep-analysis-trigger với override info

### 4. Prepare XThinking Handoff

Tạo xthinking-handoff-brief document:
- request_id: SOP code + timestamp
- department: từ charter
- analysis_type: "topic" (domain analysis)
- context: charter_summary + okr_summary + industry_context
- sop_requirements: title, type, scope, key_questions
- deep_analysis_trigger: copy từ step 2
- evidence: gathered evidence
- confidence_score: từ deep-analysis-trigger
- need_review: false (unless low confidence)

### 5. Handoff to XThinking

Gửi xthinking-handoff-brief cho vibe-xthinking-orchestrator:
- Đây là handoff point — xthinking sẽ phân tích domain
- Đợi analysis result từ xthinking

### 6. Generate SOP from Analysis

Dựa trên analysis result từ xthinking:
- Pick template từ kb/templates/ phù hợp
- Fill IPO+ICOM từ analysis + charter
- Cross-reference với KB và analysis insights
- Để [DO_USER_SPECIFY] cho critical parameters

### 7. User Review

Present draft SOP + analysis summary cho user:
- Show analysis highlights từ xthinking
- Highlight [DO_USER_SPECIFY] fields
- Record user edits + verbatim evidence

### 8. Validation

Run both schema validations:
- `schema/sop-content.schema.json`
- `schema/sop-metadata.schema.json`

If errors → show user, let fix, re-validate.

### 9. Final Output

Emit 2 artifacts (sop-content + sop-metadata) với:
- evidence: array of {claim, verbatim_quote, source}
- confidence_score: number 0-1
- need_review: boolean
