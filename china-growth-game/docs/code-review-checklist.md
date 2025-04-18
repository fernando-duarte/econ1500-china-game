# Code Review Checklist

This document outlines the required checks for reviewing code changes in the China Growth Game project.

## General Requirements

- [ ] Code follows established patterns in the codebase
- [ ] Changes are focused on the specific task/feature
- [ ] No unrelated changes or "scope creep"
- [ ] No duplication of existing functionality
- [ ] Error handling is implemented appropriately
- [ ] Performance considerations are addressed
- [ ] Security best practices are followed
- [ ] Changes pass all automated tests
- [ ] Documentation is updated to match changes

## Code Style and Quality

- [ ] Code follows style guides (ESLint/Prettier for JS, Black/Flake8 for Python)
- [ ] Variable and function names are descriptive and use consistent naming conventions
- [ ] Complex logic includes comments explaining "why" not just "what"
- [ ] No hard-coded values (use constants/configuration)
- [ ] Functions are single-purpose and focused
- [ ] No unused variables, imports, or dead code
- [ ] No commented-out code
- [ ] No debug artifacts left in code (console.log, print statements)
- [ ] Clean code organization (imports grouped, logical file structure)
- [ ] Commits are atomic and have clear messages

## Functional Requirements

- [ ] Changes meet the acceptance criteria specified in task
- [ ] Edge cases are handled (empty inputs, large datasets, etc.)
- [ ] State mutations are handled safely
- [ ] Async operations are properly managed (proper error handling, loading states)
- [ ] Browser compatibility considerations (if applicable)
- [ ] Mobile responsiveness (if applicable)

## Testing

- [ ] Unit tests cover new functionality
- [ ] Edge cases are tested
- [ ] Existing tests pass
- [ ] Test coverage is adequate
- [ ] Integration tests cover key workflows (if applicable)
- [ ] UI tests for critical paths (if applicable)

## Performance

- [ ] API responses are efficient and optimized
- [ ] Database queries are optimized
- [ ] No N+1 problems in data fetching
- [ ] Expensive operations are minimized
- [ ] Memory usage is reasonable
- [ ] Bundle size impact is considered (for frontend)
- [ ] Rendering performance is acceptable (for frontend)

## Security

- [ ] Input validation and sanitization
- [ ] No sensitive data exposure
- [ ] Authentication/authorization checks in place
- [ ] CSRF protection (if applicable)
- [ ] SQL/NoSQL injection prevention
- [ ] XSS prevention
- [ ] Secure HTTP headers configured
- [ ] Environment-specific configurations properly separated

## Accessibility (Frontend)

- [ ] Semantic HTML is used appropriately
- [ ] ARIA attributes used correctly where needed
- [ ] Color contrast meets WCAG 2.1 AA standards
- [ ] Keyboard navigation works as expected
- [ ] Screen reader compatibility
- [ ] Focus management implemented correctly
- [ ] Images have alt text
- [ ] Form elements have proper labels
- [ ] Error messages are accessible

## User Experience (Frontend)

- [ ] Design matches specifications/mockups
- [ ] Loading states are handled properly
- [ ] Error states are handled properly
- [ ] Empty states are handled properly
- [ ] Transitions and animations are smooth
- [ ] Responsive layout works on various screen sizes
- [ ] Interactive elements have appropriate hover/focus states
- [ ] User flow is intuitive and logical

## Economic Model (Backend)

- [ ] Economic equations are implemented correctly
- [ ] Model matches the specifications in documentation
- [ ] Edge cases in economic simulation are handled
- [ ] Performance of calculations is optimized
- [ ] Numerical stability is ensured
- [ ] Data persistence is implemented correctly
- [ ] Serialization/deserialization of model state works
- [ ] Model state can be replayed deterministically

## Release Readiness

- [ ] Feature flags are properly used (if applicable)
- [ ] Database migrations are included (if applicable)
- [ ] Environment-specific configurations are updated
- [ ] Dependency changes are documented
- [ ] Breaking changes are documented
- [ ] Deployment steps are documented
- [ ] Monitoring and alerting considerations

## Ownership Assignment

For modules split at 200-300 lines, the ownership should be clearly defined. Each module should have:

- A clearly defined purpose and responsibility
- Documentation of inputs, outputs, and side effects
- Assigned primary and secondary maintainers
- Clear integration points with other modules

When a module needs to be split:
1. Create a proposal in the issue tracker
2. Identify logical boundaries for separation
3. Assign owners to the new modules
4. Implement the split with appropriate tests
5. Update documentation to reflect the new structure 