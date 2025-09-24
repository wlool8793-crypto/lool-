"""
API Performance Benchmarks

This module contains comprehensive benchmarks for API endpoints to measure
response times, throughput, and resource usage.
"""

import asyncio
import json
import time
import statistics
from typing import Dict, List, Any
import aiohttp
import pytest
import psutil
import numpy as np
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key"
TEST_USER_ID = "benchmark-user"
TEST_SESSION_ID = "benchmark-session"

# Benchmark configuration
WARMUP_REQUESTS = 10
BENCHMARK_REQUESTS = 100
CONCURRENT_USERS = [1, 5, 10, 20, 50]

class APIBenchmark:
    """API benchmarking utility class"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.results = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def warmup(self):
        """Warm up the API with initial requests"""
        print("Warming up API...")
        for _ in range(WARMUP_REQUESTS):
            await self._make_request(f"{self.base_url}/health")

    async def _make_request(self, url: str, method: str = "GET",
                          data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """Make a single HTTP request and return metrics"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        try:
            request_headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            if headers:
                request_headers.update(headers)

            async with self.session.request(method, url, json=data, headers=request_headers) as response:
                content = await response.text()
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss

                return {
                    "status_code": response.status,
                    "response_time": (end_time - start_time) * 1000,  # Convert to ms
                    "memory_usage": end_memory - start_memory,
                    "success": response.status < 400,
                    "content_length": len(content),
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            end_time = time.time()
            return {
                "status_code": 0,
                "response_time": (end_time - start_time) * 1000,
                "memory_usage": 0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def benchmark_endpoint(self, endpoint: str, method: str = "GET",
                               data: Dict = None, concurrent_users: int = 10) -> Dict:
        """Benchmark a single endpoint with concurrent users"""
        print(f"Benchmarking {endpoint} with {concurrent_users} concurrent users...")

        url = f"{self.base_url}{endpoint}"

        # Create concurrent requests
        tasks = []
        for _ in range(BENCHMARK_REQUESTS):
            tasks.append(self._make_request(url, method, data))

        # Execute requests concurrently
        results = await asyncio.gather(*tasks)

        # Calculate statistics
        successful_results = [r for r in results if r["success"]]

        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            memory_usage = [r["memory_usage"] for r in successful_results]

            stats = {
                "endpoint": endpoint,
                "method": method,
                "concurrent_users": concurrent_users,
                "total_requests": len(results),
                "successful_requests": len(successful_results),
                "success_rate": len(successful_results) / len(results),
                "response_time_stats": {
                    "min": min(response_times),
                    "max": max(response_times),
                    "mean": statistics.mean(response_times),
                    "median": statistics.median(response_times),
                    "stdev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                    "p95": np.percentile(response_times, 95),
                    "p99": np.percentile(response_times, 99),
                },
                "memory_stats": {
                    "mean": statistics.mean(memory_usage),
                    "max": max(memory_usage),
                    "min": min(memory_usage),
                },
                "throughput": len(successful_results) / (sum(response_times) / 1000),  # requests/second
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "concurrent_users": concurrent_users,
                "total_requests": len(results),
                "successful_requests": 0,
                "success_rate": 0,
                "error": "All requests failed",
                "timestamp": datetime.utcnow().isoformat()
            }

        return stats

    async def run_all_benchmarks(self):
        """Run benchmarks for all API endpoints"""
        await self.warmup()

        # Define endpoints to benchmark
        endpoints = [
            ("/health", "GET", None),
            ("/api/v1/chat", "POST", {
                "message": "Benchmark test message",
                "user_id": TEST_USER_ID,
                "session_id": TEST_SESSION_ID
            }),
            ("/api/v1/agent/execute", "POST", {
                "task": "Benchmark task execution",
                "context": {"user_id": TEST_USER_ID},
                "tools": ["web_search"]
            }),
            (f"/api/v1/memory/{TEST_USER_ID}", "GET", None),
            ("/api/v1/sessions", "GET", None),
            ("/api/v1/analytics", "GET", None),
        ]

        # Run benchmarks for different concurrency levels
        all_results = []

        for endpoint, method, data in endpoints:
            endpoint_results = []

            for concurrent in CONCURRENT_USERS:
                result = await self.benchmark_endpoint(endpoint, method, data, concurrent)
                endpoint_results.append(result)

                # Print immediate results
                print(f"  {endpoint} ({method}) - {concurrent} users: "
                      f"Mean: {result.get('response_time_stats', {}).get('mean', 0):.2f}ms, "
                      f"Success: {result.get('success_rate', 0)*100:.1f}%")

            all_results.append({
                "endpoint": endpoint,
                "method": method,
                "results": endpoint_results
            })

        self.results = {
            "benchmark_summary": {
                "base_url": self.base_url,
                "benchmark_requests": BENCHMARK_REQUESTS,
                "concurrent_users": CONCURRENT_USERS,
                "timestamp": datetime.utcnow().isoformat(),
                "total_endpoints": len(endpoints)
            },
            "endpoint_results": all_results
        }

        return self.results

    def generate_report(self) -> str:
        """Generate a comprehensive benchmark report"""
        if not self.results:
            return "No benchmark results available"

        report = []
        report.append("# API Performance Benchmark Report")
        report.append(f"Generated: {datetime.utcnow().isoformat()}")
        report.append("")

        # Summary statistics
        report.append("## Summary")
        summary = self.results["benchmark_summary"]
        report.append(f"- Base URL: {summary['base_url']}")
        report.append(f"- Total Endpoints: {summary['total_endpoints']}")
        report.append(f"- Requests per Endpoint: {summary['benchmark_requests']}")
        report.append(f"- Concurrency Levels: {summary['concurrent_users']}")
        report.append("")

        # Endpoint results
        report.append("## Endpoint Results")
        report.append("")

        for endpoint_result in self.results["endpoint_results"]:
            endpoint = endpoint_result["endpoint"]
            method = endpoint_result["method"]
            report.append(f"### {method} {endpoint}")
            report.append("")

            # Create table for different concurrency levels
            report.append("| Concurrent Users | Success Rate | Mean Response Time | P95 Response Time | Throughput |")
            report.append("|------------------|--------------|-------------------|-------------------|------------|")

            for result in endpoint_result["results"]:
                concurrent = result["concurrent_users"]
                success_rate = result["success_rate"] * 100
                mean_time = result.get("response_time_stats", {}).get("mean", 0)
                p95_time = result.get("response_time_stats", {}).get("p95", 0)
                throughput = result.get("throughput", 0)

                report.append(f"| {concurrent} | {success_rate:.1f}% | {mean_time:.2f}ms | {p95_time:.2f}ms | {throughput:.2f} req/s |")

            report.append("")

        # Performance analysis
        report.append("## Performance Analysis")
        report.append("")

        # Find best and worst performing endpoints
        all_stats = []
        for endpoint_result in self.results["endpoint_results"]:
            for result in endpoint_result["results"]:
                if result["success_rate"] > 0:
                    all_stats.append({
                        "endpoint": endpoint_result["endpoint"],
                        "method": endpoint_result["method"],
                        "concurrent": result["concurrent_users"],
                        "mean_time": result.get("response_time_stats", {}).get("mean", float('inf')),
                        "success_rate": result["success_rate"],
                        "throughput": result.get("throughput", 0)
                    })

        if all_stats:
            best_performance = min(all_stats, key=lambda x: x["mean_time"])
            worst_performance = max(all_stats, key=lambda x: x["mean_time"])
            highest_throughput = max(all_stats, key=lambda x: x["throughput"])

            report.append(f"**Best Performance:** {best_performance['method']} {best_performance['endpoint']} "
                         f"({best_performance['concurrent']} users) - {best_performance['mean_time']:.2f}ms")
            report.append("")
            report.append(f"**Worst Performance:** {worst_performance['method']} {worst_performance['endpoint']} "
                         f"({worst_performance['concurrent']} users) - {worst_performance['mean_time']:.2f}ms")
            report.append("")
            report.append(f"**Highest Throughput:** {highest_throughput['method']} {highest_throughput['endpoint']} "
                         f"({highest_throughput['concurrent']} users) - {highest_throughput['throughput']:.2f} req/s")
            report.append("")

        # Recommendations
        report.append("## Recommendations")
        report.append("")

        # Analyze results and provide recommendations
        slow_endpoints = [s for s in all_stats if s["mean_time"] > 1000]
        low_success_endpoints = [s for s in all_stats if s["success_rate"] < 0.95]

        if slow_endpoints:
            report.append("### Slow Endpoints (>1s)")
            for endpoint in slow_endpoints:
                report.append(f"- {endpoint['method']} {endpoint['endpoint']}: {endpoint['mean_time']:.2f}ms")
            report.append("")
            report.append("Consider:")
            report.append("- Optimizing database queries")
            report.append("- Implementing caching")
            report.append("- Adding connection pooling")
            report.append("- Scaling horizontally")
            report.append("")

        if low_success_endpoints:
            report.append("### Low Success Rate Endpoints (<95%)")
            for endpoint in low_success_endpoints:
                report.append(f"- {endpoint['method']} {endpoint['endpoint']}: {endpoint['success_rate']*100:.1f}%")
            report.append("")
            report.append("Consider:")
            report.append("- Improving error handling")
            report.append("- Increasing timeout values")
            report.append("- Adding retry mechanisms")
            report.append("- Monitoring system resources")
            report.append("")

        return "\n".join(report)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_api_benchmarks(benchmark):
    """Run API benchmarks"""
    async with APIBenchmark() as benchmark_runner:
        results = await benchmark_runner.run_all_benchmarks()

        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_benchmark_results_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        # Generate and save report
        report = benchmark_runner.generate_report()
        report_filename = f"api_benchmark_report_{timestamp}.md"

        with open(report_filename, 'w') as f:
            f.write(report)

        print(f"Benchmark results saved to {filename}")
        print(f"Benchmark report saved to {report_filename}")

        # Return results for further analysis
        return results


if __name__ == "__main__":
    # Run benchmarks when script is executed directly
    asyncio.run(test_api_benchmarks(None))