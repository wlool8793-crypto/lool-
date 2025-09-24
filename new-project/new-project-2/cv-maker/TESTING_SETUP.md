# CV Maker Testing Setup and Configuration

This document outlines the comprehensive testing setup and configuration for the CV Maker application.

## Testing Framework Overview

The CV Maker application uses a multi-layered testing approach:

- **Unit Tests**: Vitest with React Testing Library for component and utility testing
- **Integration Tests**: Vitest for testing component interactions and workflows
- **End-to-End Tests**: Playwright for testing complete user journeys
- **Accessibility Tests**: Jest-axe for WCAG 2.1 compliance testing
- **Performance Tests**: Custom utilities for performance benchmarking

## Installation and Setup

### Prerequisites

```bash
# Ensure Node.js 18+ is installed
node --version

# Ensure npm is installed
npm --version
```

### Install Dependencies

```bash
# Install all testing dependencies
npm install

# Install Playwright browsers
npx playwright install
```

## Test Configuration Files

### Vitest Configuration (`vitest.config.ts`)

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    reporters: ['verbose'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/coverage/**',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/contexts': path.resolve(__dirname, './src/contexts'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/lib': path.resolve(__dirname, './src/lib'),
    },
  },
});
```

### Playwright Configuration (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './src/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Running Tests

### Unit and Integration Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- PersonalInfoStep.test.tsx
```

### End-to-End Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run E2E tests headed (visible browser)
npm run test:e2e:headed

# Run specific E2E test
npm run test:e2e -- --grep "CV Creation Workflow"
```

### Accessibility Tests

```bash
# Accessibility tests are included in unit tests
npm test -- accessibility-suite.test.tsx

# Run tests with accessibility focus
npm test -- --testNamePattern="accessibility"
```

### Performance Tests

```bash
# Performance tests are included in unit tests
npm test -- --testNamePattern="performance"
```

## Test Structure

### Directory Structure

```
src/
├── __tests__/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.test.tsx
│   │   │   ├── card.test.tsx
│   │   │   ├── modal.test.tsx
│   │   │   └── ...
│   │   ├── common/
│   │   │   ├── Input.test.tsx
│   │   │   └── ...
│   │   └── FormSteps/
│   │       └── PersonalInfoStep.test.tsx
│   ├── contexts/
│   │   └── CVContext.test.tsx
│   ├── utils/
│   │   ├── validation.test.ts
│   │   └── fileHandler.test.ts
│   └── accessibility/
│       └── accessibility-suite.test.tsx
├── e2e/
│   ├── cv-creation.spec.ts
│   ├── marriage-biodata.spec.ts
│   └── ...
├── test/
│   ├── setup.ts
│   ├── utils.ts
│   ├── accessibility.ts
│   ├── performance.ts
│   └── types.ts
└── ...
```

### Test Utilities

#### Custom Render Function

```typescript
import { render, RenderOptions } from '@testing-library/react';
import { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

export function renderWithProviders(
  ui: ReactElement,
  { ...renderOptions }: RenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <BrowserRouter>
        <I18nextProvider i18n={i18n}>
          {children}
        </I18nextProvider>
      </BrowserRouter>
    );
  }
  return { ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}
```

#### Mock Utilities

```typescript
// Mock file data for testing
export const createMockFile = (name: string, type: string, size: number = 1024): File => {
  const blob = new Blob(['mock file content'], { type });
  return new File([blob], name, { type });
};

// Mock image data for testing
export const createMockImage = (width: number = 100, height: number = 100): string => {
  return `data:image/svg+xml;base64,${btoa(
    `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="${width}" height="${height}" fill="#ccc"/>
    </svg>`
  )}`;
};
```

## Test Coverage

### Coverage Goals

- **Overall Coverage**: 80% minimum
- **Critical Components**: 90% minimum
- **Utility Functions**: 95% minimum
- **Form Components**: 85% minimum

### Coverage Reports

Coverage reports are generated in the `coverage/` directory:

```bash
# View HTML coverage report
open coverage/index.html

# View coverage for specific files
npm run test:coverage -- --coverage-reporter=text
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Testing and Quality Assurance

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:coverage

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
```

## Best Practices

### Writing Tests

1. **Test User Behavior, Not Implementation**
   ```typescript
   // Good
   expect(screen.getByText('Welcome')).toBeInTheDocument()

   // Bad
   expect(component.state().isVisible).toBe(true)
   ```

2. **Use Semantic Queries**
   ```typescript
   // Good
   screen.getByRole('button', { name: 'Submit' })

   // Bad
   screen.getByTestId('submit-button')
   ```

3. **Test Accessibility Automatically**
   ```typescript
   const results = await axe(container);
   expect(results).toHaveNoViolations();
   ```

4. **Mock External Dependencies**
   ```typescript
   vi.mock('@/contexts/CVContext', () => ({
     useCV: () => ({
       state: mockState,
       dispatch: mockDispatch,
     }),
   }));
   ```

### Performance Testing

```typescript
import { testComponentPerformance } from '@/test/performance';

it('performs well under load', async () => {
  const stats = await testComponentPerformance('Button', 100, () => {
    const { container, unmount } = render(<Button>Test</Button>);
    unmount();
  });

  expect(stats.avg).toBeLessThan(5);
  expect(stats.max).toBeLessThan(10);
});
```

### Accessibility Testing

```typescript
import { testAccessibility } from '@/test/accessibility';

it('meets WCAG 2.1 standards', async () => {
  const { container } = render(<Component />);
  await testAccessibility(container);
});
```

## Debugging Tests

### Debug Mode

```bash
# Run tests with debug mode
npm test -- --debug

# Run tests with verbose output
npm test -- --verbose
```

### Playwright Debug Mode

```bash
# Run Playwright with UI for debugging
npm run test:e2e:ui

# Run Playwright in headed mode
npm run test:e2e:headed

# Run specific test with debug
npm run test:e2e -- --debug
```

### Common Issues

1. **Act Warnings**: Use `await act()` for state updates
2. **Missing Providers**: Use `renderWithProviders` instead of `render`
3. **Async Operations**: Use `waitFor` for async operations
4. **Mock Setup**: Ensure mocks are properly set up and cleaned up

## Test Documentation

### Component Tests

Each component should have tests covering:
- Rendering with different props
- User interactions
- Accessibility compliance
- Performance characteristics
- Error handling

### Integration Tests

Integration tests should cover:
- Multi-step form workflows
- Context provider interactions
- Data flow between components
- Error scenarios

### E2E Tests

E2E tests should cover:
- Complete user journeys
- Cross-browser compatibility
- Mobile responsiveness
- Performance under load
- Error recovery

## Maintenance

### Keeping Tests Updated

1. **Review Coverage Reports**: Regularly check coverage reports
2. **Update Snapshots**: Update snapshots when UI changes intentionally
3. **Refactor Tests**: Keep tests DRY and maintainable
4. **Add New Tests**: Add tests for new features and components

### Test Performance

- Use test.parallel for independent tests
- Use test.describe for grouping related tests
- Use test.step for breaking down complex tests
- Mock expensive operations

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use the provided test utilities
3. Include accessibility tests
4. Add performance benchmarks
5. Document complex test scenarios

## Resources

- [React Testing Library Documentation](https://testing-library.com/docs/react-testing-library/intro/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Jest-axe Documentation](https://github.com/nickcolley/jest-axe)
- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)