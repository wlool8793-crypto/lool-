import { ReactNode } from 'react';

// Test utility types
export interface TestWrapperProps {
  children: ReactNode;
}

export interface MockFile {
  name: string;
  type: string;
  size: number;
  content?: string;
}

export interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  componentSize: number;
}

export interface AccessibilityResult {
  violations: any[];
  passes: any[];
  incomplete: any[];
  inapplicable: any[];
}

export interface TestConfig {
  includeAccessibility?: boolean;
  includePerformance?: boolean;
  includeVisual?: boolean;
  timeout?: number;
  retries?: number;
}

export interface E2ETestScenario {
  name: string;
  description: string;
  steps: E2ETestStep[];
  expectedResults: string[];
}

export interface E2ETestStep {
  action: string;
  selector?: string;
  value?: string;
  waitFor?: string;
  timeout?: number;
}

export interface ComponentTestSuite {
  componentName: string;
  unitTests: string[];
  integrationTests: string[];
  accessibilityTests: string[];
  performanceTests: string[];
}

export interface CoverageReport {
  total: number;
  covered: number;
  percentage: number;
  files: {
    [key: string]: {
      total: number;
      covered: number;
      percentage: number;
    };
  };
}