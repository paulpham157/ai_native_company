# ADR 0003: Integration Testing Strategy

## Status
Accepted

## Context
Integration tests cần validate handoff giữa skills. Ban đầu có 2 approaches:

**Approach A: Chỉ dùng synthetic-data/**
- Tạo deterministic test data trong synthetic-data/
- 100% reproducible, easy debugging
- Không capture real-world edge cases
- Có thể miss bugs chỉ xuất hiện với real data

**Approach B: Chỉ dùng examples/**
- Dùng real examples từ existing company structures
- Capture real-world scenarios
- Không deterministic (examples có thể change)
- Harder debugging với data noise

## Decision
Chọn **hybrid approach**: synthetic-data/ + examples/

### Test Coverage
1. **Schema contract validation** (automated) - Validate emit đúng evidence/confidence format
2. **Handoff correctness** (output → input mapping) - Validate output của skill A match input schema của skill B
3. **Error recovery** (skill failure handling) - Validate nếu skill A fail, skill B recover đúng cách

### Test Data Strategy
- **synthetic-data/** - Deterministic tests cho core workflows
- **examples/** - Smoke tests với real data từ sample-company

### Rationale
- Synthetic-data đảm bảo deterministic behavior cho CI/CD
- Examples capture real-world complexity synthetic không thể predict
- Coverage both happy path và edge cases
- Fast feedback với synthetic, regression protection với examples

## Consequences

### Positive
- Best của cả worlds: deterministic + realistic
- Fast CI với synthetic-data
- Regression protection với examples
- Good coverage cho edge cases

### Negative
- Maintaining 2 test datasets
- Examples có thể change và break tests
- Slower test suite so với chỉ synthetic

### Mitigations
- Version-lock examples data
- Separate test suites: fast (synthetic) vs slow (examples)
- CI run fast suite on every commit, slow suite nightly
- Clear ownership cho each dataset
