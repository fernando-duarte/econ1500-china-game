# Testing Policy: Mocks and Stubs

- Mocks and stubs are **only allowed in test code** (unit/integration tests, CI).
- Never use stubbing, fake data, or mocking patterns in code that runs in dev or prod environments.
- All external service mocking (e.g., API, DB, secrets) must be limited to test files and CI jobs.
- Dev and prod environments must always use real services and data sources.
- This ensures that tests are reliable, but production and development are always realistic and auditable. 