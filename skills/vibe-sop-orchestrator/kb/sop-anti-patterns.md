# SOP Anti-Patterns

> Common mistakes khi tạo SOP và cách tránh. Reference cho cả Quick và Deep mode.

## Anti-Pattern 1: Vague Process Steps

```diff
- Step 1: Xử lý content
+ Step 1: Review draft content theo style guide
```

**Vấn đề:** "Xử lý" không mô tả hành động cụ thể. Ai làm? Làm gì? Bao lâu?

**Fix:** Dùng action verb cụ thể: Review, Approve, Submit, Validate, Export.

## Anti-Pattern 2: Ghost Input

Input không có source rõ ràng hoặc source không tồn tại:

```json
{
  "inputs": [{"name": "Draft", "source": "Team", "format": "markdown"}]
}
```

**Vấn đề:** "Team" không phải source cụ thể. Ai trong team?

**Fix:** Ghi rõ role/system: "Content Writer", "CMS System", "Client email".

## Anti-Pattern 3: Missing Controls

SOP operational không có controls:

```json
{
  "controls": []
}
```

**Vấn đề:** Operational SOP không có quality gate = chaos.

**Fix:** Ít nhất 1 control: style guide, QC checklist, compliance policy.

## Anti-Pattern 4: Fake Evidence

```diff
- "evidence": [{"claim": "Process đã được duyệt", "source": "internal"}]
+ "evidence": [{"claim": "Process đã được duyệt", "verbatim_quote": "Quy trình này đã được CEO duyệt ngày 15/06", "source": "MKT charter v2.1"}]
```

**Vấn đề:** `source: "internal"` không traceable. `verbatim_quote` missing.

**Fix:** Luôn có verbatim_quote + source file cụ thể.

## Anti-Pattern 5: Circular Dependencies

```
SOP-MKT-001 → depends_on → SOP-MKT-002 → depends_on → SOP-MKT-001
```

**Vấn đề:** Không thể execute được.

**Fix:** Dùng `relation: "related_to"` thay vì `depends_on` cho reciprocal relationships.

## Anti-Pattern 6: Over-Engineering Documentation

```diff
- Step 1: Mở email
- Step 2: Click "Soạn thảo"
- Step 3: Nhập nội dung
+ Step 1: Soạn email phản hồi theo template chuẩn
```

**Vấn đề:** Documentation SOP không cần từng click chuột — focus vào quyết định, không phải thao tác.

## Anti-Pattern 7: Confidence Inflation

Gán confidence_score > 0.8 mà không có evidence verbatim:

**Vấn đề:** Hallucination — AI tự tin sai.

**Fix:** Confidence max 0.6 nếu không có verbatim quote. 0.5 nếu chỉ assumption.
