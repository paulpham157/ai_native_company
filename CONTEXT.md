# Context - AI Native Company Skills

> Domain language và glossary cho hệ thống skills AI Native Company v2.0.0

---

## Core Philosophy

### Trần sao âm vậy
Triết lý thiết kế theo mô hình công ty thực tế. Sao chép tối đa cấu trúc, quy trình, và best practices từ doanh nghiệp thực thay vì phát minh lại. Áp dụng ở mọi level: company structure, SOP templates, AI worker profiles.

---

## Skill Architecture

### 8 Components
Cấu trúc chuẩn cho mọi skill v2.0.0:
1. `SKILL.md` - Core workflow và documentation
2. `skill.json` - Machine-readable metadata
3. `kb/` - Knowledge base (templates, rubrics, frameworks)
4. `script/` - Validation và utility scripts
5. `prompt/` - Prompt templates
6. `schema/` - JSON schemas cho validation
7. `test/` - Test suite
8. `synthetic-data/` - Sample data cho testing

### Schema Contract
Quy ước integration giữa skills:
- `enforces_8_components` - Bắt buộc 8 components structure
- `emits_evidence_confidence` - Skill phải emit evidence, confidence_score, need_review cho outputs
- `handoff_brief_schema` - Schema chuẩn cho handoff giữa skills

### Evidence/Confidence/Need Review
Ba trường bắt buộc cho outputs có tính criticality (OKRs, Quality Standards, SOPs):
- `evidence` - Data hoặc reasoning support kết luận
- `confidence_score` - Độ tin cậy (0-1), threshold default 0.7
- `need_review` - Boolean flag nếu confidence thấp hoặc evidence yếu

---

## SOP (Standard Operating Procedure)

### Quick Mode
Mode tạo SOP đơn giản: clone template + fill info từ department charter + OKRs + existing knowledge base. Dùng cho SOPs routine, ít cross-department, low risk.

### Deep Mode
Mode tạo SOP phức tạp: gọi vibe-xthinking-orchestrator để phân tích sâu industry/domain trước khi generate SOP. Dùng cho SOPs high impact, nhiều dependencies, cần domain expertise.

### Mode Selection Rubric
Criteria để chọn Quick vs Deep mode:
- **Quick mode:** SOP đơn giản, routine, ít cross-department, low risk
- **Deep mode:** SOP phức tạp, high impact, nhiều dependencies, cần domain expertise
- **User override:** Luôn cho phép user chọn mode bất kể recommendation

---

## Multi-Agent Pattern

### Hybrid Approach (MODE TOPIC)
Execution pattern cho vibe-xthinking-orchestrator MODE TOPIC:
- **Phase 1 (Sequential):** Agent 1 (Researcher) thu thập thông tin
- **Phase 2 (Parallel):** Agents 2, 3, 4 (Explicit Thinker, Value Chain Analyst, Synthesizer) chạy parallel
- **Phase 3 (Sequential):** Agent 5 (Validator) validate và emit evidence/confidence
- **Checkpoints:** User có thể intervene giữa các phases

### Single-Agent Pattern
Execution pattern cho MODE PROBLEM và MODE DECISION:
- Single agent với systematic frameworks (5 Whys, Fishbone, Eisenhower Matrix, RICE)
- Cần thiết cho tính immediate và consistency
- Focus speed over depth cho one-off tasks

---

## Universal Reviewer

### Artifact Types Supported
vibe-review có thể review: Markdown, JSON, YAML configuration files

### Auto-Detection
Detect artifact type based on file extension

### Fallback Behavior
Nếu unsupported type → warning + skip (không error)

### Extension Point
Cho phép thêm custom reviewers cho new types qua config

---

## Integration Testing

### Test Coverage
1. Schema contract validation (automated)
2. Handoff correctness (output → input mapping)
3. Error recovery (skill failure handling)

### Test Data Strategy
- `synthetic-data/` - Deterministic tests
- `examples/` - Smoke tests với real data

---

## Build Strategy

### Parallel Build
Build song song các phần độc lập:
- Schemas
- Knowledge base templates
- Scripts (symlink)

### Sequential Build
Build tuần tự các phần có dependency:
- SKILL.md workflow
- Integration tests

---

## Script Reuse

### Symlink Strategy
Symlink scripts từ vibe-company-orchestrator (validator.py, anonymizer.py, log_helper.py, review_queue.py, install_hooks.sh) thay vì copy. Symlink đơn giản nhất, Windows cũng hỗ trợ.

---

## Handoff Brief

### Schema
Schema chuẩn cho handoff giữa skills, defined trong `handoff_brief_schema` field của skill.json

### Flow
Output của skill A → validate qua handoff_brief_schema → input của skill B
