"""
Performance Testing Suite for StarHub Communications Generator

Tests backend API performance, database query performance, and load handling.
"""

import time
import statistics
import asyncio
from typing import List, Dict
import httpx
from concurrent.futures import ThreadPoolExecutor


BASE_URL = "http://localhost:8000"

# Test data
SAMPLE_CAMPAIGN = {
    "channel": "email",
    "cohorts": ["deal_seekers", "mass_market"],
    "product_line": "homehub_plus",
    "objective": "promotion",
    "promotion_details": "Test promotion for performance testing",
    "tone": "friendly",
    "custom_instructions": "Keep it short and engaging",
    "required_phrases": ["test", "performance"],
    "prohibited_words": []
}


class PerformanceMetrics:
    """Store and calculate performance metrics"""

    def __init__(self):
        self.response_times: List[float] = []
        self.success_count = 0
        self.failure_count = 0
        self.errors: List[str] = []

    def add_result(self, response_time: float, success: bool, error: str = None):
        """Add a test result"""
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            if error:
                self.errors.append(error)

    def get_statistics(self) -> Dict:
        """Calculate statistics"""
        if not self.response_times:
            return {}

        sorted_times = sorted(self.response_times)
        return {
            "total_requests": len(self.response_times),
            "successful": self.success_count,
            "failed": self.failure_count,
            "min_time": min(self.response_times),
            "max_time": max(self.response_times),
            "mean_time": statistics.mean(self.response_times),
            "median_time": statistics.median(self.response_times),
            "p95_time": sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0,
            "p99_time": sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0,
        }

    def print_report(self, test_name: str):
        """Print formatted performance report"""
        stats = self.get_statistics()

        print(f"\n{'='*60}")
        print(f"Performance Test: {test_name}")
        print(f"{'='*60}")

        if not stats:
            print("No data collected")
            return

        print(f"Total Requests:    {stats['total_requests']}")
        print(f"Successful:        {stats['successful']} ({stats['successful']/stats['total_requests']*100:.1f}%)")
        print(f"Failed:            {stats['failed']} ({stats['failed']/stats['total_requests']*100:.1f}%)")
        print(f"\nResponse Times (seconds):")
        print(f"  Min:             {stats['min_time']:.3f}s")
        print(f"  Mean:            {stats['mean_time']:.3f}s")
        print(f"  Median:          {stats['median_time']:.3f}s")
        print(f"  Max:             {stats['max_time']:.3f}s")
        print(f"  95th percentile: {stats['p95_time']:.3f}s")
        print(f"  99th percentile: {stats['p99_time']:.3f}s")

        if self.errors:
            print(f"\nErrors encountered:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")


def test_api_health():
    """Test 1: API Health Check - Should be very fast"""
    print("\n" + "="*60)
    print("TEST 1: API Health Check")
    print("="*60)
    print("Requirement: < 100ms response time")

    metrics = PerformanceMetrics()

    for i in range(10):
        try:
            start_time = time.time()
            response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
            end_time = time.time()

            response_time = end_time - start_time
            success = response.status_code == 200

            metrics.add_result(response_time, success)

            if not success:
                metrics.add_result(response_time, False, f"HTTP {response.status_code}")

        except Exception as e:
            metrics.add_result(1.0, False, str(e))

    metrics.print_report("API Health Check")

    stats = metrics.get_statistics()
    if stats['mean_time'] < 0.1:
        print("✅ PASS: Mean response time < 100ms")
    else:
        print(f"❌ FAIL: Mean response time {stats['mean_time']*1000:.1f}ms exceeds 100ms threshold")

    return metrics


def test_campaign_creation():
    """Test 2: Campaign Creation - Should be < 2s"""
    print("\n" + "="*60)
    print("TEST 2: Campaign Creation Performance")
    print("="*60)
    print("Requirement: < 2 seconds response time (95th percentile)")

    metrics = PerformanceMetrics()

    # Test 20 campaign creations
    for i in range(20):
        try:
            start_time = time.time()
            response = httpx.post(
                f"{BASE_URL}/campaigns/",
                json=SAMPLE_CAMPAIGN,
                timeout=10.0
            )
            end_time = time.time()

            response_time = end_time - start_time
            success = response.status_code == 200

            metrics.add_result(response_time, success)

            if not success:
                metrics.add_result(response_time, False, f"HTTP {response.status_code}: {response.text[:100]}")

        except Exception as e:
            metrics.add_result(5.0, False, str(e))

    metrics.print_report("Campaign Creation")

    stats = metrics.get_statistics()
    if stats['p95_time'] < 2.0:
        print("✅ PASS: 95th percentile < 2 seconds")
    else:
        print(f"❌ FAIL: 95th percentile {stats['p95_time']:.3f}s exceeds 2s threshold")

    return metrics


def test_database_queries():
    """Test 3: Database Query Performance - Should be < 500ms"""
    print("\n" + "="*60)
    print("TEST 3: Database Query Performance")
    print("="*60)
    print("Requirement: < 500ms response time")

    # First create some test campaigns
    campaign_ids = []
    for i in range(5):
        try:
            response = httpx.post(
                f"{BASE_URL}/campaigns/",
                json=SAMPLE_CAMPAIGN,
                timeout=10.0
            )
            if response.status_code == 200:
                campaign_ids.append(response.json()["id"])
        except Exception as e:
            print(f"Warning: Could not create test campaign: {e}")

    if not campaign_ids:
        print("❌ FAIL: Could not create test campaigns for database query testing")
        return None

    metrics = PerformanceMetrics()

    # Test 1: List all campaigns
    for i in range(10):
        try:
            start_time = time.time()
            response = httpx.get(f"{BASE_URL}/campaigns/", timeout=5.0)
            end_time = time.time()

            response_time = end_time - start_time
            success = response.status_code == 200

            metrics.add_result(response_time, success)

        except Exception as e:
            metrics.add_result(1.0, False, str(e))

    # Test 2: Get individual campaigns
    for campaign_id in campaign_ids:
        try:
            start_time = time.time()
            response = httpx.get(f"{BASE_URL}/campaigns/{campaign_id}", timeout=5.0)
            end_time = time.time()

            response_time = end_time - start_time
            success = response.status_code == 200

            metrics.add_result(response_time, success)

        except Exception as e:
            metrics.add_result(1.0, False, str(e))

    metrics.print_report("Database Queries")

    stats = metrics.get_statistics()
    if stats['mean_time'] < 0.5:
        print("✅ PASS: Mean query time < 500ms")
    else:
        print(f"❌ FAIL: Mean query time {stats['mean_time']*1000:.0f}ms exceeds 500ms threshold")

    return metrics


def test_concurrent_requests():
    """Test 4: Concurrent Request Handling - 5 simultaneous users"""
    print("\n" + "="*60)
    print("TEST 4: Concurrent Request Handling")
    print("="*60)
    print("Requirement: Handle 5 simultaneous requests without errors")

    metrics = PerformanceMetrics()

    def make_request(request_id: int) -> tuple:
        """Make a single request"""
        try:
            start_time = time.time()
            response = httpx.post(
                f"{BASE_URL}/campaigns/",
                json={**SAMPLE_CAMPAIGN, "promotion_details": f"Concurrent test {request_id}"},
                timeout=15.0
            )
            end_time = time.time()

            return (end_time - start_time, response.status_code == 200, None)
        except Exception as e:
            return (10.0, False, str(e))

    # Execute 5 concurrent requests
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(5)]
        results = [future.result() for future in futures]

    for response_time, success, error in results:
        metrics.add_result(response_time, success, error)

    metrics.print_report("Concurrent Requests")

    stats = metrics.get_statistics()
    if stats['successful'] == 5:
        print("✅ PASS: All concurrent requests successful")
    else:
        print(f"❌ FAIL: Only {stats['successful']}/5 concurrent requests succeeded")

    if stats['max_time'] < 5.0:
        print("✅ PASS: Max response time under load < 5s")
    else:
        print(f"⚠️  WARNING: Max response time {stats['max_time']:.3f}s exceeds 5s")

    return metrics


def test_generation_endpoint():
    """Test 5: Generation Endpoint Performance - Should be < 10s"""
    print("\n" + "="*60)
    print("TEST 5: Communication Generation Performance")
    print("="*60)
    print("Requirement: < 10 seconds end-to-end generation time")
    print("Note: This test requires valid ANTHROPIC_API_KEY")
    print("Skipping actual API calls to avoid costs - testing endpoint structure only")

    # Create a campaign first
    try:
        response = httpx.post(
            f"{BASE_URL}/campaigns/",
            json=SAMPLE_CAMPAIGN,
            timeout=10.0
        )
        if response.status_code != 200:
            print("❌ FAIL: Could not create test campaign")
            return None

        campaign_id = response.json()["id"]
        print(f"✅ Campaign created: {campaign_id}")

    except Exception as e:
        print(f"❌ FAIL: Error creating campaign: {e}")
        return None

    # Note: Not actually calling generate endpoint to avoid API costs
    # In real testing, you would uncomment below:

    # metrics = PerformanceMetrics()
    # try:
    #     start_time = time.time()
    #     response = httpx.post(
    #         f"{BASE_URL}/campaigns/{campaign_id}/generate",
    #         timeout=30.0
    #     )
    #     end_time = time.time()
    #
    #     response_time = end_time - start_time
    #     success = response.status_code == 200
    #
    #     metrics.add_result(response_time, success)
    #
    #     if response_time < 10.0:
    #         print("✅ PASS: Generation completed in < 10 seconds")
    #     else:
    #         print(f"❌ FAIL: Generation took {response_time:.1f}s (> 10s threshold)")
    #
    # except Exception as e:
    #     print(f"❌ FAIL: Generation error: {e}")

    print("⚠️  MANUAL TEST REQUIRED: Test generation endpoint with valid API key")
    print(f"   POST {BASE_URL}/campaigns/{campaign_id}/generate")
    print("   Expected: < 10 seconds response time")

    return None


def main():
    """Run all performance tests"""
    print("\n" + "="*60)
    print("STARHUB COMMUNICATIONS GENERATOR - PERFORMANCE TEST SUITE")
    print("="*60)
    print(f"Testing endpoint: {BASE_URL}")
    print("Ensure backend is running before executing tests")

    # Check if backend is accessible
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        if response.status_code != 200:
            print(f"\n❌ ERROR: Backend not accessible at {BASE_URL}")
            print("Please start backend with: ./start-backend.sh")
            return
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to backend at {BASE_URL}")
        print(f"Error: {e}")
        print("Please start backend with: ./start-backend.sh")
        return

    print("✅ Backend is accessible\n")

    # Run all tests
    results = {
        "health": test_api_health(),
        "campaign_creation": test_campaign_creation(),
        "database": test_database_queries(),
        "concurrent": test_concurrent_requests(),
        "generation": test_generation_endpoint(),
    }

    # Summary
    print("\n" + "="*60)
    print("PERFORMANCE TEST SUMMARY")
    print("="*60)

    print("\nAcceptance Criteria Status:")
    print(f"  Backend API response < 2s (95th):  {'✅' if results['campaign_creation'] and results['campaign_creation'].get_statistics()['p95_time'] < 2.0 else '❌'}")
    print(f"  Database queries < 500ms:          {'✅' if results['database'] and results['database'].get_statistics()['mean_time'] < 0.5 else '❌'}")
    print(f"  Concurrent requests (5 users):     {'✅' if results['concurrent'] and results['concurrent'].get_statistics()['successful'] == 5 else '❌'}")
    print(f"  Generation < 10s:                  ⚠️  MANUAL TEST REQUIRED")

    print("\n" + "="*60)
    print("Testing complete. Review results above.")
    print("="*60)


if __name__ == "__main__":
    main()
