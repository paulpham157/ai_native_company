# SOP Naming & Versioning Conventions

> Quy ước đặt tên SOP code, phiên bản, và quản lý dependencies. Đồng bộ với `sop-metadata.schema.json`.

## SOP Code Format

```
SOP-{DEPT}-{NNN}
```

| Component | Ý nghĩa | Ví dụ |
|-----------|---------|-------|
| `SOP` | Prefix cố định | SOP |
| `{DEPT}` | Mã department (3 ký tự) | MKT, HR, ENG, FIN, OPS |
| `{NNN}` | Số thứ tự (001-999) | 001, 042, 123 |

**Regex:** `^SOP-[A-Z0-9]{3}-\d{3}$`

### Department Codes

| Code | Department |
|------|-----------|
| MKT | Marketing |
| HR | Human Resources |
| ENG | Engineering |
| FIN | Finance |
| OPS | Operations |
| SAL | Sales |
| CS | Customer Success |
| PD | Product |
| LEG | Legal |
| DSN | Design |

## Versioning

### Version Format

Semantic versioning: `{major}.{minor}`

| Bump | Khi nào | Ví dụ |
|------|---------|-------|
| Major | Thay đổi process, adds/removes steps | 1.0 → 2.0 |
| Minor | Cập nhật control, mechanism, clarification | 1.0 → 1.1 |

### Change History

Mỗi version bump phải ghi vào `change_history`:

```json
{
  "version": "1.1",
  "date": "2026-06-15",
  "author": "Content Lead",
  "summary": "Thêm compliance check step sau review"
}
```

## SOP Types

| Type | Usage | Version cadence |
|------|-------|----------------|
| `operational` | Quy trình vận hành hàng ngày | Major: 6-12 tháng |
| `documentation-only` | Hướng dẫn, tham khảo | Major: 12-24 tháng |

## Dependency Management

Dependencies giữa các SOP:

```json
{
  "sop_code": "SOP-MKT-003",
  "dependencies": [
    {"sop_code": "SOP-MKT-001", "relation": "precedes"},
    {"sop_code": "SOP-ENG-002", "relation": "depends_on"},
    {"sop_code": "SOP-MKT-004", "relation": "related_to"}
  ]
}
```

| Relation | Ý nghĩa |
|----------|---------|
| `precedes` | SOP này chạy trước SOP kia |
| `depends_on` | SOP này cần SOP kia hoàn thành trước |
| `related_to` | Liên quan nhưng không có thứ tự |
