#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class TestRunner {
  constructor() {
    this.results = {
      unit: { passed: 0, failed: 0, total: 0, coverage: 0 },
      e2e: { passed: 0, failed: 0, total: 0 },
      accessibility: { passed: 0, failed: 0, total: 0 },
      performance: { passed: 0, failed: 0, total: 0 },
    };
    this.startTime = Date.now();
    this.outputDir = path.join(__dirname, '../test-results');
  }

  async run() {
    console.log('🚀 Starting CV Maker Test Suite\n');

    try {
      // Create output directory
      if (!fs.existsSync(this.outputDir)) {
        fs.mkdirSync(this.outputDir, { recursive: true });
      }

      // Run unit tests with coverage
      await this.runUnitTests();

      // Run E2E tests
      await this.runE2ETests();

      // Run accessibility tests
      await this.runAccessibilityTests();

      // Run performance tests
      await this.runPerformanceTests();

      // Generate comprehensive report
      await this.generateReport();

      // Display results
      this.displayResults();

      // Exit with appropriate code
      const hasFailures = Object.values(this.results).some(category => category.failed > 0);
      process.exit(hasFailures ? 1 : 0);

    } catch (error) {
      console.error('❌ Test runner failed:', error.message);
      process.exit(1);
    }
  }

  async runUnitTests() {
    console.log('📦 Running Unit Tests...');

    try {
      // Run unit tests with coverage
      execSync('npm run test:coverage -- --reporter=verbose', {
        stdio: 'pipe',
        encoding: 'utf-8'
      });

      // Parse coverage results
      this.parseCoverageResults();

      console.log('✅ Unit tests completed successfully\n');

    } catch (error) {
      console.error('❌ Unit tests failed:', error.message);
      this.results.unit.failed += 1;
    }
  }

  async runE2ETests() {
    console.log('🎭 Running End-to-End Tests...');

    try {
      // Run E2E tests
      execSync('npm run test:e2e', {
        stdio: 'pipe',
        encoding: 'utf-8'
      });

      console.log('✅ E2E tests completed successfully\n');

    } catch (error) {
      console.error('❌ E2E tests failed:', error.message);
      this.results.e2e.failed += 1;
    }
  }

  async runAccessibilityTests() {
    console.log('♿ Running Accessibility Tests...');

    try {
      // Run accessibility-specific tests
      execSync('npm test -- --testNamePattern="accessibility" --reporter=verbose', {
        stdio: 'pipe',
        encoding: 'utf-8'
      });

      console.log('✅ Accessibility tests completed successfully\n');

    } catch (error) {
      console.error('❌ Accessibility tests failed:', error.message);
      this.results.accessibility.failed += 1;
    }
  }

  async runPerformanceTests() {
    console.log('⚡ Running Performance Tests...');

    try {
      // Run performance-specific tests
      execSync('npm test -- --testNamePattern="performance" --reporter=verbose', {
        stdio: 'pipe',
        encoding: 'utf-8'
      });

      console.log('✅ Performance tests completed successfully\n');

    } catch (error) {
      console.error('❌ Performance tests failed:', error.message);
      this.results.performance.failed += 1;
    }
  }

  parseCoverageResults() {
    try {
      const coveragePath = path.join(__dirname, '../coverage/coverage-summary.json');
      if (fs.existsSync(coveragePath)) {
        const coverageData = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
        this.results.unit.coverage = coverageData.total.statements.pct;
        this.results.unit.passed = coverageData.total.statements.covered;
        this.results.unit.total = coverageData.total.statements.total;
      }
    } catch (error) {
      console.warn('⚠️ Could not parse coverage results:', error.message);
    }
  }

  async generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      duration: Date.now() - this.startTime,
      results: this.results,
      summary: {
        totalPassed: Object.values(this.results).reduce((sum, cat) => sum + cat.passed, 0),
        totalFailed: Object.values(this.results).reduce((sum, cat) => sum + cat.failed, 0),
        totalTests: Object.values(this.results).reduce((sum, cat) => sum + cat.total, 0),
        overallCoverage: this.results.unit.coverage,
      },
      recommendations: this.generateRecommendations(),
    };

    const reportPath = path.join(this.outputDir, 'test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    // Generate HTML report
    await this.generateHTMLReport(report);
  }

  generateRecommendations() {
    const recommendations = [];

    if (this.results.unit.coverage < 80) {
      recommendations.push('Increase unit test coverage to 80% or higher');
    }

    if (this.results.e2e.failed > 0) {
      recommendations.push('Fix failing E2E tests to ensure user journeys work correctly');
    }

    if (this.results.accessibility.failed > 0) {
      recommendations.push('Address accessibility violations to meet WCAG 2.1 standards');
    }

    if (this.results.performance.failed > 0) {
      recommendations.push('Optimize performance bottlenecks identified in tests');
    }

    return recommendations;
  }

  async generateHTMLReport(report) {
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Maker Test Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .header h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 1.1em;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .test-categories {
            margin-bottom: 40px;
        }
        .category {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .category-header {
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
            font-size: 1.1em;
        }
        .category-content {
            padding: 20px;
        }
        .test-stats {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        .recommendations {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
        }
        .recommendations h3 {
            margin-top: 0;
            color: #856404;
        }
        .recommendations ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .recommendations li {
            margin-bottom: 5px;
            color: #856404;
        }
        .status-passed {
            color: #28a745;
        }
        .status-failed {
            color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CV Maker Test Report</h1>
            <div class="timestamp">
                Generated: ${new Date(report.timestamp).toLocaleString()}<br>
                Duration: ${(report.duration / 1000).toFixed(2)} seconds
            </div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="value">${report.summary.totalTests}</div>
            </div>
            <div class="summary-card">
                <h3>Passed</h3>
                <div class="value status-passed">${report.summary.totalPassed}</div>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <div class="value status-failed">${report.summary.totalFailed}</div>
            </div>
            <div class="summary-card">
                <h3>Coverage</h3>
                <div class="value">${report.summary.overallCoverage.toFixed(1)}%</div>
            </div>
        </div>

        <div class="test-categories">
            <div class="category">
                <div class="category-header">
                    📦 Unit Tests
                    <span class="${report.results.unit.failed === 0 ? 'status-passed' : 'status-failed'}">
                        ${report.results.unit.failed === 0 ? '✅ Passed' : '❌ Failed'}
                    </span>
                </div>
                <div class="category-content">
                    <div class="test-stats">
                        <span>${report.results.unit.passed} / ${report.results.unit.total} passed</span>
                        <span>${report.results.unit.coverage.toFixed(1)}% coverage</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${report.results.unit.coverage}%"></div>
                    </div>
                </div>
            </div>

            <div class="category">
                <div class="category-header">
                    🎭 End-to-End Tests
                    <span class="${report.results.e2e.failed === 0 ? 'status-passed' : 'status-failed'}">
                        ${report.results.e2e.failed === 0 ? '✅ Passed' : '❌ Failed'}
                    </span>
                </div>
                <div class="category-content">
                    <div class="test-stats">
                        <span>${report.results.e2e.passed} / ${report.results.e2e.total} passed</span>
                        <span>Browser compatibility tests</span>
                    </div>
                </div>
            </div>

            <div class="category">
                <div class="category-header">
                    ♿ Accessibility Tests
                    <span class="${report.results.accessibility.failed === 0 ? 'status-passed' : 'status-failed'}">
                        ${report.results.accessibility.failed === 0 ? '✅ Passed' : '❌ Failed'}
                    </span>
                </div>
                <div class="category-content">
                    <div class="test-stats">
                        <span>${report.results.accessibility.passed} / ${report.results.accessibility.total} passed</span>
                        <span>WCAG 2.1 compliance</span>
                    </div>
                </div>
            </div>

            <div class="category">
                <div class="category-header">
                    ⚡ Performance Tests
                    <span class="${report.results.performance.failed === 0 ? 'status-passed' : 'status-failed'}">
                        ${report.results.performance.failed === 0 ? '✅ Passed' : '❌ Failed'}
                    </span>
                </div>
                <div class="category-content">
                    <div class="test-stats">
                        <span>${report.results.performance.passed} / ${report.results.performance.total} passed</span>
                        <span>Performance benchmarks</span>
                    </div>
                </div>
            </div>
        </div>

        ${report.recommendations.length > 0 ? `
        <div class="recommendations">
            <h3>📋 Recommendations</h3>
            <ul>
                ${report.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
        ` : ''}
    </div>
</body>
</html>
    `;

    const htmlPath = path.join(this.outputDir, 'test-report.html');
    fs.writeFileSync(htmlPath, html);
    console.log('📊 HTML report generated:', htmlPath);
  }

  displayResults() {
    console.log('📊 Test Results Summary\n');
    console.log('═'.repeat(50));

    Object.entries(this.results).forEach(([category, results]) => {
      const icon = results.failed === 0 ? '✅' : '❌';
      const coverage = category === 'unit' ? ` (${results.coverage.toFixed(1)}% coverage)` : '';
      console.log(`${icon} ${category.toUpperCase()}: ${results.passed}/${results.total} passed${coverage}`);
    });

    console.log('═'.repeat(50));

    const totalPassed = Object.values(this.results).reduce((sum, cat) => sum + cat.passed, 0);
    const totalFailed = Object.values(this.results).reduce((sum, cat) => sum + cat.failed, 0);
    const totalTests = Object.values(this.results).reduce((sum, cat) => sum + cat.total, 0);

    console.log(`📈 Overall: ${totalPassed}/${totalTests} tests passed (${((totalPassed/totalTests)*100).toFixed(1)}%)`);
    console.log(`⏱️  Duration: ${(Date.now() - this.startTime) / 1000}s`);

    if (totalFailed > 0) {
      console.log(`\n❌ ${totalFailed} test(s) failed. Check the reports for details.`);
    } else {
      console.log(`\n🎉 All tests passed!`);
    }

    console.log(`\n📄 Detailed report: ${this.outputDir}/test-report.html`);
  }
}

// Run the test suite
if (require.main === module) {
  const runner = new TestRunner();
  runner.run().catch(console.error);
}

module.exports = TestRunner;