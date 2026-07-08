# E-commerce — Industry SOP Template

> Template SOP đặc thù cho e-commerce/retail environment: order processing, inventory management, customer support.

## Đặc thù

| Factor | Đặc điểm |
|--------|---------|
| Volume | High volume transactions, SOP phải scalable |
| Real-time | Order processing real-time, không delay |
| Multi-system | CMS, OMS, WMS, CRM — nhiều system integration |
| Compliance | Payment data (PCI), customer data (GDPR) |

## Điều chỉnh so với SOP chuẩn

- **Inputs:** Nhiều automated triggers (order placed → payment confirmed)
- **Process:** Event-driven, không linear — có parallel branches
- **Controls:** PCI/GDPR compliance bắt buộc
- **Mechanisms:** Heavy system integration (OMS → WMS → Shipping)
- **Duration:** SLA-driven (24h ship, 1h response)

## Ví dụ: Order Fulfillment SOP

```json
{
  "sop_code": "SOP-OPS-001",
  "title": "Order Fulfillment Process",
  "inputs": [
    {"name": "New order", "source": "Shopify", "format": "json"},
    {"name": "Payment confirmation", "source": "Payment Gateway", "format": "json"}
  ],
  "process": [
    {"step": 1, "action": "Verify payment + fraud check", "responsible": "OMS", "duration_estimate": "5m"},
    {"step": 2, "action": "Route to warehouse", "responsible": "OMS → WMS", "duration_estimate": "1m"},
    {"step": 3, "action": "Pick + pack items", "responsible": "Warehouse Team", "duration_estimate": "30m"},
    {"step": 4, "action": "Generate shipping label", "responsible": "WMS", "duration_estimate": "2m"},
    {"step": 5, "action": "Ship and update tracking", "responsible": "Carrier API", "duration_estimate": "5m"}
  ],
  "controls": [
    {"name": "PCI Data Security", "standard": "REG-PCI-001"},
    {"name": "Order Accuracy QC", "standard": "QC-OPS-001"}
  ],
  "mechanisms": [
    {"name": "Shopify OMS", "type": "system"},
    {"name": "Warehouse Management System", "type": "system"},
    {"name": "ShipStation", "type": "tool"}
  ]
}
```

## Lưu ý

- SLA external (customer-facing) luôn có buffer — SLO internal tighter
- Mọi order exception phải có escalation path
- Evidence cần quote từ operations playbook, không assumption
