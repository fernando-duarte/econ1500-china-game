# Project Rules & Code Quality

## 1. Code Ownership & Reviews
- Assign clear ownership for each module (split at 200–300 lines).
- Define a review checklist:
  - Style and formatting (see [`app.py`](../china-growth-game/economic-model/app.py), [`team-routes.js`](../china-growth-game/app/routes/team-routes.js))
  - Docstrings and documentation
  - Test coverage (see TODO: link to test suite)
  - Adherence to project rules (see [`project-rules.mdc`](../project-rules.mdc))
- Require peer review before merging changes to main branches.

## 2. Automated Quality Gates
- Enforce linting, formatting, and security checks in CI pipeline.
  - (TODO: Link to CI config files, e.g., `.github/workflows/`, `Dockerfile`, etc.)
- Set minimum test coverage thresholds (e.g., 90%).
- Block merges if quality gates fail.
- Reference existing CI config (TODO: link to config files).

## 3. Mocking & Stubbing
- Mocks and stubs are allowed only in tests and CI, never in dev or prod environments.
- External services must be mocked in CI tests for reliability.
  - See [`economic-model-service.js`](../china-growth-game/app/services/economic-model-service.js) for service abstraction.
- Document allowed mocking patterns and provide examples. (TODO: Link to test examples.)

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
- TODO: Link to CI configs and test examples. 