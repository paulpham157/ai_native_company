# IPO+ICOM Framework Reference

> Mọi SOP đều theo cấu trúc IPO (Input-Process-Output) với ICOM extension (Controls, Mechanisms, Outputs). Framework này định nghĩa từng thành phần và cách điền.

## IPO Core

### Inputs
Đầu vào cần thiết để thực thi SOP:

| Field | Ý nghĩa | Ví dụ |
|-------|---------|-------|
| `name` | Tên đầu vào | "Draft content" |
| `source` | Nguồn cung cấp | "Content Team", "CMS System" |
| `format` | Định dạng dữ liệu | `markdown`, `json`, `yaml`, `csv` |

**Nguyên tắc:** Mỗi input phải có source rõ ràng. Không input không-source.

### Process
Các bước thực thi SOP:

| Field | Ý nghĩa | Ví dụ |
|-------|---------|-------|
| `step` | Số thứ tự (1-based) | 1 |
| `action` | Mô tả hành động | "Review draft for factual accuracy" |
| `responsible` | Role/Vai trò thực hiện | "Editor", "Content Lead" |
| `duration_estimate` | Thời gian ước tính | "2h", "30m", "1d" |

**Nguyên tắc:**
- Step phải sequential, không overlapping
- Mỗi step có đúng 1 responsible party
- duration_estimate dùng format: `{number}{h|m|d}`

### Outputs
Kết quả sau khi thực thi SOP:

| Field | Ý nghĩa | Ví dụ |
|-------|---------|-------|
| `name` | Tên output | "Approved content" |
| `destination` | Nơi output được gửi đến | "Publishing", "CMS" |
| `format` | Định dạng output | `markdown`, `json`, `yaml`, `csv` |

**Nguyên tắc:** Output destination phải tồn tại trong system. Không output vào "nowhere".

## ICOM Extensions

### Controls (C)
Ràng buộc, tiêu chuẩn, policy mà SOP phải tuân theo:

| Field | Ý nghĩa | Ví dụ |
|-------|---------|-------|
| `name` | Tên control | "Style Guide v3", "QC-001" |
| `type` | Loại control | `policy`, `standard`, `regulation` |
| `standard` | Reference code | "QC-001", "ISO-9001" |

**Mỗi control phải traceable** — có reference cụ thể, không "theo quy định chung".

### Mechanisms (M)
Công cụ, hệ thống, role hỗ trợ thực thi SOP:

| Field | Ý nghĩa | Ví dụ |
|-------|---------|-------|
| `name` | Tên mechanism | "CMS", "Slack", "Editor" |
| `type` | Loại | `tool`, `system`, `role`, `skill` |

**Phân biệt:**
- `tool`: Software cụ thể (CMS, Excel, Figma)
- `system`: Hệ thống (ERP, CRM)
- `role`: Human role (Editor, Reviewer)
- `skill`: AI skill (vibe-aiworkforce, vibe-review)

## Ví dụ SOP hoàn chỉnh

Xem schema `schema/sop-content.schema.json` cho cấu trúc đầy đủ. Template operational và documentation có sẵn trong `kb/templates/`.
