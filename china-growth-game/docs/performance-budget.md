# Performance Budget

This document outlines performance targets for the China Growth Game application across different environments and network conditions.

## Bundle Size Budgets

| Asset Type | Budget (kb) | Enforcement |
|------------|-------------|-------------|
| Initial JS bundle | < 150kb | Error in CI build |
| Initial CSS | < 50kb | Error in CI build |
| Total initial payload | < 250kb | Error in CI build |
| Individual chunk | < 100kb | Warning in CI build |
| Image assets | < 200kb each | Warning in CI build |
| Font files | < 50kb each | Warning in CI build |

## Load Time Budgets

| Metric | Slow 3G | Fast 3G | 4G / WiFi |
|--------|---------|---------|-----------|
| First Contentful Paint (FCP) | < 3s | < 1.5s | < 1s |
| Time to Interactive (TTI) | < 5s | < 3s | < 2s |
| Total Blocking Time (TBT) | < 600ms | < 300ms | < 200ms |
| Largest Contentful Paint (LCP) | < 4s | < 2.5s | < 1.5s |
| Cumulative Layout Shift (CLS) | < 0.1 | < 0.1 | < 0.1 |

## Runtime Performance Budgets

| Metric | Target | Enforcement |
|--------|--------|-------------|
| Main thread work | < 4s | Warning |
| JS execution time | < 2s | Warning |
| Memory usage | < 60MB | Warning |
| DOM nodes | < 1500 | Warning |
| Animation frame rate | > 50fps | Warning |

## API Response Budgets

| Endpoint | Target Response Time |
|----------|----------------------|
| Game state retrieval | < 200ms |
| Team creation | < 300ms |
| Decision submission | < 250ms |
| Round advancement | < 500ms |
| Economic calculation | < 800ms |
| Leaderboard retrieval | < 150ms |

## Dashboard Performance Requirements

| Dashboard | Initial Load | Data Update | Render Time |
|-----------|--------------|-------------|-------------|
| Team Dashboard | < 1s | < 300ms | < 200ms |
| Admin Dashboard | < 1.5s | < 400ms | < 300ms |
| Economic Data Charts | < 1.2s | < 350ms | < 250ms |
| Leaderboard | < 0.8s | < 200ms | < 100ms |

## Test and Monitoring Requirements

1. All dashboard UI components must include performance testing in CI pipeline
2. Lighthouse scores must be:
   - Performance: > 85
   - Accessibility: > 90 
   - Best Practices: > 90
   - SEO: > 90

3. Real User Monitoring (RUM) must be implemented to track:
   - Page load times across different network connections
   - Time to interactive for critical pages
   - JS errors and their impact on performance

4. Synthetic monitoring should run hourly to detect performance regressions

## Enforcement Methods

1. Bundle size monitoring via webpack-bundle-analyzer
2. Load time metrics via Lighthouse CI
3. Runtime budgets monitored via Performance API
4. API response times measured with server timing headers
5. Dashboard render times tracked via React Profiler

## Improvement Process

1. Weekly performance review of monitoring data
2. Prioritize fixes for any metric exceeding 120% of budget
3. Performance regression tests must pass before merging PRs
4. Monthly review and adjustment of budgets based on real-world data 