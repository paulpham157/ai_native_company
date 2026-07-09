# Thinking Anti-Patterns — vibe-xthinking-orchestrator

> **Common mistakes cần tránh trong explicit thinking.**

## Anti-Pattern 1: Confirmation Bias

**Symptom:** Chỉ tìm evidence ủng hộ hypothesis, ignore contradicting data.

**Fix:**
- Explicitly seek disconfirming evidence
- Record all assumptions với challenge field
- Cross-validate từ multiple perspectives

## Anti-Pattern 2: Analysis Paralysis

**Symptom:** Thu thập quá nhiều data nhưng không đưa ra conclusion.

**Fix:**
- Set timebox cho mỗi phase
- Force recommendation even with incomplete data
- Use confidence score để indicate uncertainty

## Anti-Pattern 3: False Precision

**Symptom:** Sử dụng số liệu chính xác giả tạo (e.g., "confidence_score: 0.8472").

**Fix:**
- Confidence scores chỉ cần 2 decimal places
- Prefer ranges over exact numbers
- Document methodology cho mọi số liệu

## Anti-Pattern 4: Single Source Dependency

**Symptom:** Mọi claims dựa trên 1 source duy nhất.

**Fix:**
- Yêu cầu ≥ 2 sources cho critical claims
- Flag single-source claims trong evidence chain
- Reduce confidence cho single-source claims

## Anti-Pattern 5: Ignoring Assumptions

**Symptom:** Không document assumptions, dẫn đến conclusions sai.

**Fix:**
- Mọi analysis bắt đầu với assumptions list
- Mỗi assumption có confidence score
- Review assumptions trước khi kết luận

## Anti-Pattern 6: Causal Oversimplification

**Symptom:** Quy problem phức tạp về 1 root cause duy nhất.

**Fix:**
- Use Fishbone cho complex problems
- Document causal relationships
- Consider system interactions
