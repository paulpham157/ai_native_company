# SOP Quality Rubric

> Rubric đánh giá chất lượng SOP artifact sau khi tạo. Dùng để self-review trước khi emit evidence/confidence_score/need_review.

## Quality Dimensions

| Dimension | Trọng số | 1★ (Kém) | 3★ (Đạt) | 5★ (Xuất sắc) |
|-----------|---------|---------|----------|--------------|
| Input completeness | 2 | Thiếu input, không source | Đủ input nhưng source mơ hồ | Input rõ ràng, source traceable |
| Process clarity | 3 | Steps mơ hồ, thiếu action | Steps rõ, thiếu duration | Steps chi tiết, có duration, responsible rõ |
| Output traceability | 2 | Output không destination | Output có destination chung chung | Output destination cụ thể, measurable |
| Control coverage | 2 | Thiếu controls | Có controls nhưng vague | Controls standard reference rõ ràng |
| Evidence quality | 3 | Không evidence | Có evidence nhưng paraphrase | Verbatim quote từ charter |

## Scoring

| Tổng weighted score | Đánh giá | Action |
|--------------------|----------|--------|
| 40-50 | Excellent | Emit confidence >= 0.8 |
| 25-39 | Acceptable | Emit confidence 0.5-0.7, review nếu operational |
| < 25 | Poor | Emit confidence < 0.5, need_review = true, sửa lại |

## Quick Checklist

- [ ] Mọi input có source cụ thể
- [ ] Mỗi step có action verb rõ ràng (không "xử lý", "làm")
- [ ] Output destination measurable
- [ ] Controls có standard reference
- [ ] Evidence là verbatim quote (không paraphrase)
- [ ] confidence_score >= 0.7 cho operational SOP
