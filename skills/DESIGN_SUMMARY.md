# Design Summary: Missing Skills Implementation

> **Document này tóm tắt tất cả decisions đã thống nhất qua 20 câu hỏi phỏng vấn về việc tái tạo 3 skills còn thiếu: vibe-sop-orchestrator, vibe-xthinking-orchestrator, và vibe-review.**

---

## Overview

**Skills cần build:**
1. `vibe-sop-orchestrator` - Tạo/sửa SOP đơn lẻ theo template chuẩn
2. `vibe-xthinking-orchestrator` - Explicit thinking, phân tích sâu industry/domain
3. `vibe-review` - Review chất lượng SOP, policy, quality gate

**Build order:** vibe-sop-orchestrator → vibe-xthinking-orchestrator → vibe-review

**Approach:** Build song song các phần độc lập (schemas, kb templates, scripts) nhưng build tuần tự các phần có dependency (SKILL.md workflow, integration tests)

---

## 1. vibe-sop-orchestrator

### Core Architecture
- **2 modes:** Quick mode (clone template + fill info) vs Deep mode (gọi vibe-xthinking-orchestrator)
- **8 components:** SKILL.md, skill.json, kb/, script/, prompt/, schema/, test/, synthetic-data/
- **Script reuse:** Symlink scripts từ vibe-company-orchestrator (validator.py, anonymizer.py, log_helper.py, review_queue.py, install_hooks.sh) - symlink đơn giản nhất, Windows cũng hỗ trợ

### Schemas
- `sop-content.schema.json` - Validate nội dung SOP (đúng format template)
- `sop-metadata.schema.json` - Validate frontmatter (sop_id, department, version, v.v.)
- `deep-analysis-trigger.schema.json` - Output schema cho decision logic: { needs_deep_analysis: boolean, confidence: number, reasoning: string, complexity_score: number }, emit evidence/confidence

### Integration Points
```json
"integrations": {
  "upstream": ["vibe-company-orchestrator"],
  "downstream": ["vibe-xthinking-orchestrator", "vibe-review"],
  "schema_contract": {
    "enforces_8_components": true,
    "emits_evidence_confidence": ["sop-content", "sop-metadata", "deep-analysis-trigger"],
    "handoff_brief_schema": "./schema/xthinking-handoff-brief.schema.json"
  }
}
```

### Knowledge Base (kb/)
```
kb/
├── sop-template.md              ← Template chuẩn (copy từ examples)
├── sop-quality-rubric.md        ← Rubric đánh giá chất lượng SOP
├── mode-selection-rubric.md     ← Rubric chọn Quick vs Deep mode
├── industry-sop-templates/      ← Templates theo industry
│   ├── tech-startup.md
│   ├── consulting.md
│   ├── ecommerce.md
└── sop-anti-patterns.md        ← Common mistakes cần tránh
```

### Workflow Phases
1. Input analysis - Parse user request, xác định department, scope, complexity
2. **Mode selection** (QUAN TRỌNG NHẤT) - Quick mode vs Deep mode theo rubric:
   - **Quick mode khi:** SOP đơn giản, routine, ít cross-department, low risk
   - **Deep mode khi:** SOP phức tạp, high impact, nhiều dependencies, cần domain expertise
   - **User override:** Luôn cho phép user chọn mode bất kể recommendation
3. Template selection - Chọn template phù hợp từ kb/ hoặc custom
4. **SOP generation** (QUAN TRỌNG NHẤT) - Fill template, apply "trần sao âm vậy":
   - Template structure copy từ examples/ (SOPs đã được validate)
   - Content fill dựa trên: department charter + OKRs + existing knowledge base
   - User review và adjust trước khi finalize
   - AI không tự ý điền critical parameters (deadlines, SLAs, KPI targets) - những cái này cần user input
5. Deep analysis (optional) - Nếu cần → gọi vibe-xthinking-orchestrator
6. Validation - Validate qua schemas, emit evidence/confidence
7. Quality gate - Gọi vibe-review
8. Output - Write SOP file + execution log

### Build Order (Internal)
1. Schemas trước (sop-content, sop-metadata)
2. SKILL.md (core workflow)
3. kb/ (templates, rubrics, anti-patterns)
4. script/ (symlink từ vibe-company-orchestrator)
5. prompt/ + test/ + synthetic-data/
6. Integration test với vibe-company-orchestrator

---

## 2. vibe-xthinking-orchestrator

### Core Architecture
- **3 modes:** MODE TOPIC, MODE PROBLEM, MODE DECISION
- **MODE TOPIC:** Multi-agent pattern với 5 agents (Researcher, Explicit Thinker, Value Chain Analyst, Synthesizer, Validator)
- **MODE PROBLEM:** Single-agent với systematic framework (5 Whys, Fishbone, Root Cause Analysis) - single-agent cần thiết cho tính immediate và consistency
- **MODE DECISION:** Single-agent với decision matrix framework (Eisenhower Matrix, RICE, v.v.) - single-agent cần thiết cho tính immediate và consistency

### Schemas
```
schema/
├── topic-analysis.schema.json      ← Output của MODE TOPIC
├── problem-analysis.schema.json    ← Output của MODE PROBLEM  
├── decision-analysis.schema.json   ← Output của MODE DECISION
├── explicit-thinking.schema.json   ← Common schema cho explicit thinking outline
└── evidence-tracking.schema.json   ← Common schema cho evidence/confidence
```

### Integration Points
```json
"integrations": {
  "upstream": ["vibe-company-orchestrator", "vibe-sop-orchestrator"],
  "downstream": ["vibe-review"],
  "schema_contract": {
    "enforces_8_components": true,
    "emits_evidence_confidence": ["topic-analysis", "problem-analysis", "decision-analysis"],
    "handoff_brief_schema": "./schema/handoff-brief.schema.json"
  }
}
```

### MODE TOPIC Workflow (Multi-agent - Hybrid approach)
1. **Phase 1 (Sequential):** Agent 1: Researcher - Thu thập thông tin về industry/domain
2. **Phase 2 (Parallel):** Agents 2, 3, 4 chạy parallel trên output của Agent 1:
   - Agent 2: Explicit Thinker - Tạo explicit thinking outline (assumptions, logic chain, gaps)
   - Agent 3: Value Chain Analyst - Phân tích Porter value chain, IPO decomposition
   - Agent 4: Synthesizer - Tổng hợp findings thành actionable insights
3. **Phase 3 (Sequential):** Agent 5: Validator - Validate output, emit evidence/confidence
4. **Checkpoints:** Có checkpoint giữa mỗi phase để user có thể intervene

---

## 3. vibe-review

### Core Architecture
- **4 review methods:**
  1. Method 1: Rules-based review (grammar, format, required sections)
  2. Method 2: Schema validation (validate against JSON schemas)
  3. Method 3: Quality rubric review (clarity, completeness, accuracy)
  4. Method 4: Human-in-the-loop review (flag items cần human review)

- **2 modes:**
  - **Quick mode (--quick):** Method 1 + Method 2 (internal drafts, intermediate outputs)
  - **Full mode (--full):** All 4 methods (final deliverables, critical artifacts)

### Schemas
```
schema/
├── review-result.schema.json      ← Output của review (score, feedback, checklist)
├── quality-rubric.schema.json     ← Rubric đánh giá chất lượng
├── review-rules.schema.json        ← Rules cho Method 1
└── hitl-checklist.schema.json     ← Checklist cho Method 4
```

### Integration Points
```json
"integrations": {
  "upstream": ["vibe-company-orchestrator", "vibe-sop-orchestrator", "vibe-xthinking-orchestrator", "vibe-aiworkforce"],
  "downstream": [],
  "schema_contract": {
    "enforces_8_components": true,
    "emits_evidence_confidence": ["review-result"],
    "universal_reviewer": true
  }
}
```

**Universal reviewer flag:** Skill này có thể review bất kỳ artifact nào từ bất kỳ skill nào:
- Support: Markdown, JSON, YAML (configuration files)
- Auto-detect based on file extension
- Fallback: Nếu unsupported type → warning + skip (không error)
- Extension point: Cho phép thêm custom reviewers cho new types qua config

---

## Overall Build Plan

### Phase 1: vibe-sop-orchestrator
1. Tạo folder structure 8 components
2. Build schemas (sop-content, sop-metadata, deep-analysis-trigger)
3. Write SKILL.md với workflow (Quick vs Deep mode)
4. Create kb/ (templates, rubrics, anti-patterns)
5. Symlink scripts từ vibe-company-orchestrator
6. Write prompt/ templates
7. Create test/ + synthetic-data/
8. Test integration với vibe-company-orchestrator:
   - Schema contract validation (automated)
   - Handoff correctness (output → input mapping)
   - Error recovery (skill failure handling)
   - Use synthetic-data/ cho deterministic tests, examples/ cho smoke tests

### Phase 2: vibe-xthinking-orchestrator
1. Tạo folder structure
2. Build schemas cho 3 modes
3. Write SKILL.md với multi-agent workflow cho MODE TOPIC
4. Implement MODE PROBLEM + MODE DECISION
5. Create kb/ (explicit thinking frameworks, industry templates)
6. Test integration với vibe-sop-orchestrator:
   - Schema contract validation (automated)
   - Handoff correctness (output → input mapping)
   - Error recovery (skill failure handling)
   - Use synthetic-data/ cho deterministic tests, examples/ cho smoke tests

### Phase 3: vibe-review
1. Tạo folder structure
2. Build schemas (review-result, quality-rubric, review-rules, hitl-checklist)
3. Write SKILL.md với 4 review methods
4. Implement quick vs full modes
5. Test integration với cả 2 skills trước:
   - Schema contract validation (automated)
   - Handoff correctness (output → input mapping)
   - Error recovery (skill failure handling)
   - Use synthetic-data/ cho deterministic tests, examples/ cho smoke tests

---

## Key Decisions Summary

1. **Build order:** vibe-sop-orchestrator → vibe-xthinking-orchestrator → vibe-review (đồng ý Q1)
2. **vibe-sop-orchestrator 2 modes:** Quick vs Deep (đồng ý Q2)
3. **vibe-sop-orchestrator schemas:** 3 schemas (đồng ý Q3)
4. **vibe-sop-orchestrator integration:** upstream vibe-company-orchestrator, downstream vibe-xthinking + vibe-review (đồng ý Q4)
5. **vibe-sop-orchestrator focus:** Phase 2 (Mode selection) và Phase 4 (SOP generation) (đồng ý Q5)
6. **vibe-sop-orchestrator kb:** Templates, rubric, industry templates, anti-patterns (đồng ý Q6)
7. **vibe-sop-orchestrator scripts:** 5 scripts, symlink từ vibe-company-orchestrator (đồng ý Q7)
8. **vibe-xthinking-orchestrator modes:** 3 modes (TOPIC, PROBLEM, DECISION) (đồng ý Q8)
9. **MODE TOPIC workflow:** Multi-agent với 5 agents (đồng ý Q9)
10. **MODE PROBLEM/DECISION:** Single-agent với frameworks (đồng ý Q10)
11. **vibe-xthinking-orchestrator schemas:** 5 schemas (đồng ý Q11)
12. **vibe-xthinking-orchestrator integration:** upstream vibe-company + vibe-sop, downstream vibe-review (đồng ý Q12)
13. **vibe-review methods:** 4 methods (đồng ý Q13)
14. **vibe-review modes:** Quick (Method 1+2) vs Full (All 4) (đồng ý Q14)
15. **vibe-review schemas:** 4 schemas (đồng ý Q15)
16. **vibe-review integration:** upstream tất cả skills, downstream none, universal reviewer flag (đồng ý Q16)
17. **Overall build plan:** 3 phases theo thứ tự (đồng ý Q17)
18. **vibe-sop-orchestrator internal order:** Schemas → SKILL.md → kb → scripts → prompt/test → integration (đồng ý Q18)
19. **Build approach:** Từng skill hoàn toàn 100% trước (trừ schemas có thể song song) (đồng ý Q19)
20. **Start approach:** Tạo design summary trước khi build (đồng ý Q20)

---

## Next Steps

1. ✅ Design summary document completed
2. → Bắt đầu Phase 1: vibe-sop-orchestrator
3. → Step 1: Build schemas (sop-content.schema.json, sop-metadata.schema.json)
