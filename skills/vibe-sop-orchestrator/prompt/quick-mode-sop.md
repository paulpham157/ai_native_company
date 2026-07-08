# Quick Mode SOP — Prompt Template

> Instruction cho AI khi thực thi Quick mode workflow. Copy prompt này vào context khi user yêu cầu tạo SOP nhanh.

## Context

- Department: {{DEPARTMENT}}
- Charter: {{CHARTER_PATH}}
- OKRs: {{OKR_PATH}}
- SOP type: {{SOP_TYPE}} (operational / documentation-only)
- Industry context: {{INDUSTRY_CONTEXT}}

## Instructions

### 1. Gather Information

Read department charter + OKRs + existing KB files để hiểu domain. Trích verbatim quotes cho evidence.

### 2. Mode Selection

Run mode-selection-rubric:
- Tính weighted score
- Score < 20 → Quick mode: tiếp tục workflow
- Score >= 20 → Deep mode: suggest user chuyển Deep mode (ghi nhận override nếu user vẫn chọn Quick)

### 3. Template Selection

Pick template từ kb/templates/:
- operational → `kb/templates/sop-operational.md`
- documentation-only → `kb/templates/sop-documentation.md`
- Industry match → `kb/industry-sop-templates/{{INDUSTRY}}.md`

### 4. Content Fill Rules

**AI tự fill:**
- SOP_TITLE, SOP_CODE, DEPARTMENT, VERSION, OWNER
- PURPOSE_DESCRIPTION, SCOPE_DESCRIPTION
- INPUT_NAME/SOURCE/FORMAT
- STEP_NUMBER/ACTION/RESPONSIBLE
- OUTPUT_NAME/DESTINATION/FORMAT
- MECHANISM_NAME/TYPE
- DATE, AUTHOR

**BLOCKED — leave as [DO_USER_SPECIFY]:**
- CONTROL_STANDARD (deadlines, SLAs)
- DURATION (time estimates)
- KPI targets from OKRs
- Any deadline/hạn chót

### 5. User Review Protocol

Present draft with BLOCKED fields highlighted:
```
[DRAFT SOP — Quick Mode]
SOP Code: SOP-{{DEPT_CODE}}-001
Status: DRAFT (need user input)

⚠️ [DO_USER_SPECIFY] fields cần bạn điền:
  - Control standards: SLAs / SLOs?
  - Duration estimates: bao lâu mỗi step?
  - KPI targets: target numbers?
```

After user edits → record verbatim evidence.

### 6. Validation

Run both schema validations:
- `schema/sop-content.schema.json`
- `schema/sop-metadata.schema.json`

If errors → show user, let fix, re-validate.

### 7. Final Output

Emit 2 artifacts (sop-content + sop-metadata) với:
- evidence: array of {claim, verbatim_quote, source}
- confidence_score: number 0-1
- need_review: boolean