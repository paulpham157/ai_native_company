# Consulting — Industry SOP Template

> Template SOP đặc thù cho consulting/service environment: client-facing, deliverable-driven, nhiều review layers.

## Đặc thù

| Factor | Đặc điểm |
|--------|---------|
| Client-facing | Mọi output phải client-ready, quality absolute |
| Review layers | Multiple reviews (team lead → partner → client) |
| Deliverables | Structured documents, presentations, spreadsheets |
| Billing | Time tracking, scope management quan trọng |

## Điều chỉnh so với SOP chuẩn

- **Process steps:** Chi tiết, bao gồm review/approval gates
- **Controls:** Nhiều quality gates trước khi gửi client
- **Evidence:** Quote từ engagement letter, SOW, client brief
- **Outputs:** Luôn có destination là "Client Deliverable" + internal archive
- **Dependencies:** Chặt chẽ — các workstream phải sync

## Ví dụ: Client Deliverable Review SOP

```json
{
  "sop_code": "SOP-CON-001",
  "title": "Client Deliverable Review & Approval",
  "process": [
    {"step": 1, "action": "Prepare deliverable draft", "responsible": "Consultant", "duration_estimate": "1d"},
    {"step": 2, "action": "Peer review", "responsible": "Senior Consultant", "duration_estimate": "4h"},
    {"step": 3, "action": "Quality assurance review", "responsible": "QC Team", "duration_estimate": "2h"},
    {"step": 4, "action": "Partner approval", "responsible": "Engagement Partner", "duration_estimate": "2h"},
    {"step": 5, "action": "Submit to client", "responsible": "Engagement Manager", "duration_estimate": "30m"}
  ],
  "controls": [
    {"name": "Deliverable Quality Standard", "standard": "QC-CON-001"},
    {"name": "Client Communication Policy", "standard": "POL-CON-002"}
  ],
  "mechanisms": [
    {"name": "Google Workspace", "type": "tool"},
    {"name": "Harvest Time Tracking", "type": "tool"}
  ]
}
```

## Lưu ý

- Mọi deliverable phải có version tracking — client có thể request revision bất kỳ lúc nào
- Evidence cần bao gồm client email/meeting notes quote — không tự suy luận
- Deadline luôn kèm buffer (SLA external = thời gian thực tế x2)
