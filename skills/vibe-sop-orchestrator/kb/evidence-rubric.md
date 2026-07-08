# Evidence & Confidence Rubric — SOP Artifacts

> Rubric chấm confidence_score và gán need_review cho SOP artifacts (sop-content, sop-metadata). Mọi artifact đều emit evidence/confidence_score/need_review.

## Confidence Scoring

| Score | Ý nghĩa | Evidence yêu cầu | need_review? |
|-------|---------|-----------------|--------------|
| 0.9-1.0 | Rất chắc | Verbatim quote từ department charter + historical SOP + benchmark | No |
| 0.7-0.8 | Khá chắc | Verbatim quote từ charter/interview HOẶC SOP mẫu có sẵn | No |
| 0.5-0.6 | Yếu | Chỉ có assumption, không quote | **YES** |
| < 0.5 | Đoán | Không evidence | **YES** (BẮT BUỘC human) |

## Evidence Quy Tắc

### Verbatim Requirement

```
SAI:  evidence.claim = "Team cần approval từ editor"          (paraphrase)
ĐÚNG: evidence.verbatim_quote = "Bài viết phải có editor duyệt" (nguyên văn từ charter)
```

Validator verify quote tồn tại trong source. Không thấy → confidence -0.2.

### Evidence cho từng SOP Field

| SOP Field | Evidence cần có |
|-----------|----------------|
| `inputs[].source` | Quote từ charter về nguồn dữ liệu |
| `process[].action` | Quote mô tả bước work |
| `outputs[].destination` | Quote nơi output được dùng |
| `controls[].standard` | Reference đến policy/standard document |
| `mechanisms[].name` | Quote tool/system được dùng |

## Special Rules

### Operational SOP
- Confidence threshold: **0.7**
- Nếu process có >5 steps mà confidence < 0.7 → `need_review = true` (risk execution sai)

### Documentation-only SOP
- Confidence threshold: **0.5** (ít rủi ro hơn)
- Nếu evidence chỉ từ assumption → luôn `need_review = true`

### SOP có dependencies
- Mỗi dependency unresolved → confidence -0.1
- Ví dụ: depends_on SOP-ENG-002 mà ENG-002 chưa tồn tại → confidence -= 0.1

## Ví dụ SOP Artifact với Evidence

```json
{
  "sop_code": "SOP-MKT-001",
  "evidence": [
    {
      "claim": "Content team gửi draft cho editor",
      "verbatim_quote": "Content writer gửi bài qua CMS cho editor review",
      "source": "MKT charter v2.1",
      "location": "line 45"
    }
  ],
  "confidence_score": 0.85,
  "need_review": false
}
```
