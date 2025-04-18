# UI/UX

## 1. Performance Budgets
- Set measurable targets for dashboard and main UI:
  - Load time: <500 ms on 3G/mobile.
  - Bundle size: <100 kb for initial load.
- Use existing performance monitoring tools (see [.lighthouserc.js](../china-growth-game/.lighthouserc.js) and [CI workflow](../.github/workflows/ci.yml) for Lighthouse CI configuration).
- See UI code: [`index.html`](../china-growth-game/app/public/index.html), [`GameDashboard`](../china-growth-game/src/layouts/game/index.js)

## 2. Accessibility & Responsiveness
- Follow WCAG 2.1 guidelines for all interactive elements.
  - Use semantic HTML and ARIA attributes in [`index.html`](../china-growth-game/app/public/index.html)
  - Ensure keyboard navigation and screen reader compatibility in React components ([`GameDashboard`](../china-growth-game/src/layouts/game/index.js))
- Define mobile/tablet breakpoints and test all required stats/controls at each size.
  - See MUI theme and layout configs ([`autocomplete.js`](../china-growth-game/src/assets/theme/components/form/autocomplete.js))
- Add A11y checks to CI pipeline (see [Lighthouse accessibility checks](../.github/workflows/ci.yml#L34) that use the `lighthouse:recommended` preset which includes accessibility audits).

## 3. Feature-Flag Rollout
- Wrap new/breaking features (e.g., news/events) in feature flags.
  - Example: "Breaking News"/event logic in [`GameDashboard`](../china-growth-game/src/layouts/game/index.js) and [`index.html`](../china-growth-game/app/public/index.html)
- Feature flags must be toggleable per-class or per-user (see [`featureFlags.js`](../china-growth-game/app/config/featureFlags.js) for implementation with per-class and per-user targeting).
- Document flag management and rollout process.

## References
- [`index.html`](../china-growth-game/app/public/index.html)
- [`GameDashboard`](../china-growth-game/src/layouts/game/index.js)
- [`autocomplete.js`](../china-growth-game/src/assets/theme/components/form/autocomplete.js)
- [`featureFlags.js`](../china-growth-game/app/config/featureFlags.js) 