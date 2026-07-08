# ADR 0004: Script Reuse Symlink Strategy

## Status
Accepted

## Context

Cần reuse scripts giữa các skills để tránh duplication. Các scripts shared gồm: validator.py, anonymizer.py, log_helper.py, review_queue.py, install_hooks.sh.

Có 3 approaches cho việc reuse:

**Approach A: Copy scripts**
- Đơn giản, dễ hiểu
- Mỗi skill có bản sao riêng
- Khó maintain (fix bug cần copy lại)
- Dễ dẫn đến version drift

**Approach B: Symlink (git)**
- Git trên macOS/Linux support symlink
- File chỉ tồn tại ở 1 nơi, các skill khác refer đến
- Windows support symlink từ Windows 10 + git config core.symlinks=true
- Khi clone repo với `git clone`, symlinks được giữ nguyên

**Approach C: Git submodule**
- Có thể track version riêng
- Over-engineer cho use case này
- Complexity cao, khó debug

## Decision

Chọn **Approach B: Symlink (git)**.

### Implementation

- Scripts gốc đặt trong `skills/vibe-company-orchestrator/script/`
- Các skill khác tạo symlink: `skills/<skill>/script/<script>.py → ../../vibe-company-orchestrator/script/<script>.py`
- Symlink path là relative path để portable giữa các máy

```
skills/vibe-sop-orchestrator/script/validator.py → ../../vibe-company-orchestrator/script/validator.py
```

### Windows Compatibility

- Git for Windows support symlinks với core.symlinks=true
- Yêu cầu Windows 10+ (build 14972+)
- Cần chạy git với admin mode hoặc developer mode enabled
- Hoặc dùng `git clone -c core.symlinks=true <repo>`

## Consequences

### Positive
- Zero duplication - scripts chỉ tồn tại 1 nơi
- Bug fix ở 1 chỗ, tất cả skill đều được hưởng
- Git track symlinks như 1 file riêng
- Clean git status (không modified files ở nhiều nơi)

### Negative
- Windows dev cần config git đúng cách
- Có thể confuse dev mới không quen symlink
- Nếu xóa file gốc, symlink sẽ broken

### Mitigations
- Validation script (validate_symlinks.py) kiểm tra symlink integrity
- Document trong INSTALL.md về yêu cầu Windows
- Symlink target là relative, không absolute
- Pre-commit hook kiểm tra symlink không bị broken
