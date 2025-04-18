# Project Rules & Code Quality

## 1. Code Ownership & Reviews
- Assign clear ownership for each module (split at 200–300 lines).
- Define a review checklist:
  - Style and formatting (see [`app.py`](../china-growth-game/economic-model/app.py), [`team-routes.js`](../china-growth-game/app/routes/team-routes.js))
  - Docstrings and documentation
  - Test coverage (see [`server.test.js`](../backend/server.test.js) and [testing policy](../docs/testing-policy.md))
  - Adherence to project rules (see [`project-rules.mdc`](../project-rules.mdc))
- Require peer review before merging changes to main branches.

## 2. Automated Quality Gates
- Enforce linting, formatting, and security checks in CI pipeline.
  - CI configuration files: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
  - Docker configs: [`frontend/Dockerfile`](../frontend/Dockerfile), [`backend/Dockerfile`](../backend/Dockerfile), [`model/Dockerfile`](../model/Dockerfile)
- Set minimum test coverage thresholds (e.g., 90%).
- Block merges if quality gates fail.
- Reference existing CI config in [GitHub workflows](../.github/workflows/ci.yml).

## 3. Mocking & Stubbing
- Mocks and stubs are allowed only in tests and CI, never in dev or prod environments.
- External services must be mocked in CI tests for reliability.
  - See [`economic-model-service.js`](../china-growth-game/app/services/economic-model-service.js) for service abstraction.
- Document allowed mocking patterns and provide examples. For examples, see [`server.test.js`](../backend/server.test.js) which mocks Socket.IO connections to test server behavior.

## Review Checklist Example
- [ ] Code is modular and under 200–300 lines per file/module
- [ ] All public functions/classes have docstrings
- [ ] No duplicate logic or code
- [ ] All major functionality is covered by tests
- [ ] No stubbing or mocking in dev/prod code
- [ ] Passes linting, formatting, and security checks
- [ ] Follows project rules and documentation

## References
- [`app.py`](../china-growth-game/economic-model/app.py)
- [`team-routes.js`](../china-growth-game/app/routes/team-routes.js)
- [`economic-model-service.js`](../china-growth-game/app/services/economic-model-service.js)
- [`project-rules.mdc`](../project-rules.mdc)
- [`ci.yml`](../.github/workflows/ci.yml)
- [`server.test.js`](../backend/server.test.js) 