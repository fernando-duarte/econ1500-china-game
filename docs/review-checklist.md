# Code Review Checklist

Use this checklist for all PRs and code reviews:

- [ ] Code style follows project conventions (linted, formatted)
- [ ] All functions/classes have clear docstrings or comments
- [ ] No duplicate code or logic; existing modules are reused
- [ ] Thorough tests for all major functionality (unit, integration)
- [ ] No stubbing/mocking in dev/prod code (only in tests)
- [ ] Performance budget is respected (bundle size, load time)
- [ ] Accessibility (a11y) checks pass (axe, Lighthouse, ARIA labels)
- [ ] Feature flags are used for experimental/breaking features
- [ ] Economic model is reproducible and auditable (versioned data, deterministic replay)
- [ ] No secrets or credentials in code or .env (use secrets manager for prod)
- [ ] Documentation is updated (README, specs, diagrams) 