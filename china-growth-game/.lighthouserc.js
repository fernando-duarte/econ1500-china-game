module.exports = {
  ci: {
    collect: {
      staticDistDir: './build',
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/team',
        'http://localhost:3000/admin'
      ],
      numberOfRuns: 3,
      settings: {
        preset: 'desktop'
      },
      chromePath: '/usr/bin/google-chrome',
    },
    upload: {
      target: 'temporary-public-storage',
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'categories:performance': ['error', { minScore: 0.85 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        
        // Core Web Vitals
        'first-contentful-paint': ['error', { maxNumericValue: 1000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 1500 }],
        'interactive': ['error', { maxNumericValue: 2000 }],
        'total-blocking-time': ['error', { maxNumericValue: 200 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        
        // Accessibility checks
        'aria-valid-attr': ['error', { minScore: 1 }],
        'document-title': ['error', { minScore: 1 }],
        'html-has-lang': ['error', { minScore: 1 }],
        'label': ['error', { minScore: 1 }],
        'color-contrast': ['error', { minScore: 1 }],
        
        // Performance checks
        'resource-summary:document:size': ['error', { maxNumericValue: 250 * 1024 }],
        'resource-summary:script:size': ['error', { maxNumericValue: 300 * 1024 }],
        'resource-summary:stylesheet:size': ['error', { maxNumericValue: 100 * 1024 }],
        'resource-summary:image:size': ['error', { maxNumericValue: 500 * 1024 }],
        'resource-summary:font:size': ['error', { maxNumericValue: 150 * 1024 }],
        
        // Skipped assertions (things we're not strictly enforcing)
        'uses-responsive-images': 'off',
        'uses-webp-images': 'off',
        'offscreen-images': 'off',
        'unused-javascript': 'off',
        'tap-targets': 'warn'
      }
    },
    server: {
      port: 9000
    },
  },
}; 