# Tech Startup — Industry SOP Template

> Template SOP đặc thù cho tech startup environment: fast iteration, flat hierarchy, nhiều tool tự động.

## Đặc thù

| Factor | Đặc điểm |
|--------|---------|
| Speed | Release hàng ngày, SOP phải nhẹ, không cồng kềnh |
| Hierarchy | Flat — 1 người có thể đảm nhiều vai trò |
| Tools | Heavy automation (CI/CD, Slack, Jira, GitHub) |
| Risk | Product-market fit risk > operational risk |

## Điều chỉnh so với SOP chuẩn

- **Process steps:** Ngắn, 3-5 steps tối đa
- **Responsible:** Role-based, không tên cá nhân (team xoay vòng)
- **Controls:** Tối thiểu — chỉ compliance-critical
- **Mechanisms:** Ưu tiên automation tools (GitHub Actions, Slack bot)
- **Evidence:** Quote từ sprint retrospective hoặc engineering handbook

## Ví dụ: Deployment SOP

```json
{
  "sop_code": "SOP-ENG-001",
  "title": "Production Deployment",
  "process": [
    {"step": 1, "action": "Create release branch từ main", "responsible": "Engineer", "duration_estimate": "5m"},
    {"step": 2, "action": "Chạy CI/CD pipeline", "responsible": "GitHub Actions", "duration_estimate": "15m"},
    {"step": 3, "action": "Review test results + deploy preview", "responsible": "Engineer", "duration_estimate": "10m"},
    {"step": 4, "action": "Approve production deploy", "responsible": "Tech Lead", "duration_estimate": "5m"}
  ],
  "controls": [
    {"name": "All tests pass", "standard": "CI Gate v1"}
  ],
  "mechanisms": [
    {"name": "GitHub Actions", "type": "tool"},
    {"name": "Slack Deploy Bot", "type": "tool"}
  ]
}
```

## Lưu ý

- Startup SOP cần update thường xuyên — version minor bump hàng sprint
- Cho phép skip steps nếu risk thấp (ghi lý do vào evidence)
