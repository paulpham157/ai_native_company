# Changelog

Tất cả thay đổi quan trọng của dự án sẽ được ghi lại tại đây.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/vi/),
và [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.3] — 2026-05-17

### Thêm mới
- **Hướng dẫn cài đặt đa nền tảng** — hỗ trợ macOS và Windows
- **Script cài đặt tự động** cho Claude Code, Antigravity, OpenClaw, Codex
- **Install guide chi tiết** (`docs/install-guide.md`) — hướng dẫn từng bước cho từng ứng dụng

### Cải thiện
- **README.md** — viết lại toàn bộ bằng tiếng Việt có dấu, chuyên nghiệp
- **vibe-aiworkforce** bổ sung hệ thống quản lý chất lượng hoàn chỉnh:
  - **SOP State Machine** — quản lý quy trình với 5 trạng thái chuẩn (template → input → processing → output → archive)
  - **SLI/SLO/SLA** — quản lý chất lượng đầu ra của AI Worker (Service Level Indicator / Objective / Agreement)
  - **KRI/KPI/OKR** — quản lý mục tiêu và báo cáo hiệu suất (Key Result Indicator / Key Performance Indicator / Objectives and Key Results)
  - **Error Budget & Incident Management** — xử lý khi chất lượng không đạt SLO
- **vibe-company-orchestrator** tích hợp Porter Value Chain, Archimate, IPO, RACI

### Loại bỏ
- **vibe-aiworkforce-gps** — skill riêng cho Alobase, không phù hợp bản community. Chức năng điều phối đã tích hợp trong `vibe-aiworkforce`

---

## [1.2.0] — 2026-05-17

### Thêm mới
- **vibe-aiworkforce** skill — Xây dựng AI Workforce chuyên biệt cho doanh nghiệp
- **vibe-company-orchestrator** skill — Thiết kế toàn bộ công ty thành hệ thống SOP
- **vibe-aiworkforce-gps** skill — AI Chief of Staff điều phối task
- **KWSR Framework** — 4 lớp tổ chức: Knowledge → Workflow → Skill → Rule
- **SOP State Machine** — 5 trạng thái chuẩn cho mỗi SOP
- **Ebook** "Hướng dẫn vận hành OPC cùng A.I Workforce v1.2" (markdown + docx)
- **Sample company** AINS — công ty mẫu OPC thực tế
- **Sample second brain** — cấu trúc Second Brain cho doanh nghiệp
- README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT
- Scripts: SOP folder creation, auto-archive, migration

---

## [1.0.0] — 2026-05-01

### Thêm mới
- Mô hình AI Native Company ban đầu
- 7 Trụ cột OPC
- Mô hình chuyển đổi A.I 1+1+N
- Tài liệu khoa học AI Workforce cho SMB
