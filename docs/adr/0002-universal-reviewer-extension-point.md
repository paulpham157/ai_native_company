# ADR 0002: Universal Reviewer Extension Point

## Status
Accepted

## Context
vibe-review được thiết kế là "universal reviewer" - có thể review bất kỳ artifact từ bất kỳ skill nào. Ban đầu thiết kế hỗ trợ tất cả file types:
- Markdown files (SOPs, policies, charters)
- JSON schemas
- YAML configs
- Code files (Python, JS)
- Binary files

Support tất cả types có issues:
- Review logic khác nhau cho mỗi type
- Khó maintain khi thêm types mới
- Một số types (binary) không realistic để review
- Bloat codebase với unused reviewers

Từ chối một số types có issues:
- User có thể cần review custom types trong tương lai
- Hardcoded type list thiếu flexibility
- Lock-in vào current types

## Decision
Chọn **selective support + extension point**:
- **Support:** Markdown, JSON, YAML (configuration files)
- **Auto-detect:** Based on file extension
- **Fallback:** Nếu unsupported type → warning + skip (không error)
- **Extension point:** Cho phép thêm custom reviewers cho new types qua config

### Rationale
- Cover 90% use cases với 3 types phổ biến nhất
- Graceful degradation thay vì error on unsupported types
- Future-proof với extension mechanism
- Maintain simplicity core logic

## Consequences

### Positive
- Focus effort trên types quan trọng nhất
- Không break workflow khi gặp unsupported types
- Easy extend cho new types
- Smaller codebase

### Negative
- Not truly "universal" - chỉ support subset
- User disappointment nếu type cần thiết không supported
- Extension point complexity

### Mitigations
- Documentation rõ ràng về supported types
- Examples cho custom reviewers
- Community contribution cho new reviewers
- Fallback message helpful (suggest alternatives)
