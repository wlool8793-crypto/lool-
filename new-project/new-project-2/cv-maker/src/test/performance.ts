import { PerformanceObserver, performance } from 'perf_hooks';

// Performance testing utilities
export class PerformanceTester {
  private measurements: Map<string, number[]> = new Map();

  measure(name: string, fn: () => void | Promise<void>): number {
    const start = performance.now();

    if (fn.constructor.name === 'AsyncFunction') {
      return fn().then(() => performance.now() - start);
    }

    fn();
    return performance.now() - start;
  }

  async measureAsync(name: string, fn: () => Promise<void>): Promise<number> {
    const start = performance.now();
    await fn();
    return performance.now() - start;
  }

  addMeasurement(name: string, duration: number): void {
    if (!this.measurements.has(name)) {
      this.measurements.set(name, []);
    }
    this.measurements.get(name)!.push(duration);
  }

  getAverageTime(name: string): number {
    const times = this.measurements.get(name) || [];
    return times.reduce((sum, time) => sum + time, 0) / times.length;
  }

  getMaxTime(name: string): number {
    const times = this.measurements.get(name) || [];
    return Math.max(...times);
  }

  getMinTime(name: string): number {
    const times = this.measurements.get(name) || [];
    return Math.min(...times);
  }

  getStats(name: string) {
    const times = this.measurements.get(name) || [];
    if (times.length === 0) return null;

    const avg = this.getAverageTime(name);
    const max = this.getMaxTime(name);
    const min = this.getMinTime(name);

    return { avg, max, min, count: times.length };
  }

  reset(): void {
    this.measurements.clear();
  }
}

// Component performance testing
export const testComponentPerformance = async (
  componentName: string,
  renderCount: number = 100,
  renderFunction: () => void
) => {
  const tester = new PerformanceTester();

  for (let i = 0; i < renderCount; i++) {
    const duration = tester.measure(componentName, renderFunction);
    tester.addMeasurement(`${componentName}_render`, duration);
  }

  const stats = tester.getStats(`${componentName}_render`);

  // Performance assertions
  expect(stats!.avg).toBeLessThan(16); // Should render in less than 16ms (60fps)
  expect(stats!.max).toBeLessThan(50); // Maximum render time should be reasonable

  return stats;
};

// Memory usage testing
export const testMemoryUsage = (componentName: string, before: number, after: number) => {
  const memoryDiff = after - before;
  const memoryIncreaseMB = memoryDiff / 1024 / 1024;

  // Log memory usage for analysis
  console.log(`${componentName} memory increase: ${memoryIncreaseMB.toFixed(2)} MB`);

  // Assert reasonable memory usage (adjust threshold based on component complexity)
  expect(memoryIncreaseMB).toBeLessThan(10); // Less than 10MB increase
};

// Large dataset testing
export const testLargeDatasetHandling = async (
  componentName: string,
  datasetSizes: number[],
  testFunction: (size: number) => Promise<void>
) => {
  const results: Array<{ size: number; duration: number; success: boolean }> = [];

  for (const size of datasetSizes) {
    try {
      const start = performance.now();
      await testFunction(size);
      const duration = performance.now() - start;

      results.push({ size, duration, success: true });

      // Performance assertions for large datasets
      expect(duration).toBeLessThan(1000); // Should handle within 1 second
    } catch (error) {
      results.push({ size, duration: 0, success: false });
      throw error;
    }
  }

  return results;
};