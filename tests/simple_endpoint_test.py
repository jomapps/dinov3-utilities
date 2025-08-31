"""
Simple endpoint test that checks service availability and tests basic functionality.
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

class SimpleEndpointTester:
    def __init__(self, base_url="http://localhost:3012"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.results = []
        
    def test_endpoint(self, method, endpoint, data=None, files=None, timeout=30):
        """Test a single endpoint with error handling."""
        url = f"{self.api_base}{endpoint}" if endpoint.startswith('/') else f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, data=data, files=files, timeout=timeout)
                else:
                    response = requests.post(url, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=timeout)
            
            duration = time.time() - start_time
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "duration_ms": round(duration * 1000, 2),
                "response_size": len(response.content),
                "error": None
            }
            
            try:
                result["response_data"] = response.json()
            except:
                result["response_data"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
            
            self.results.append(result)
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            print(f"{status} {method} {endpoint} ({response.status_code}) - {result['duration_ms']}ms")
            
            return result
            
        except requests.exceptions.ConnectionError:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "success": False,
                "duration_ms": 0,
                "response_size": 0,
                "error": "Connection refused - service not running"
            }
            self.results.append(result)
            print(f"✗ ERROR {method} {endpoint} - Service not available")
            return result
            
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "success": False,
                "duration_ms": 0,
                "response_size": 0,
                "error": str(e)
            }
            self.results.append(result)
            print(f"✗ ERROR {method} {endpoint} - {str(e)}")
            return result

    def run_basic_tests(self):
        """Run basic endpoint tests to verify service functionality."""
        print("DINOv3 Service Basic Endpoint Tests")
        print("=" * 50)
        print(f"Testing service at: {self.base_url}")
        print()
        
        # Test service availability
        print("1. Testing Service Availability")
        root_result = self.test_endpoint("GET", "/")
        
        if not root_result["success"]:
            print("\n❌ Service is not running or not accessible")
            print("Please start the service with: python -m uvicorn app.main:app --host 0.0.0.0 --port 3012")
            return False
        
        print("✅ Service is running")
        print()
        
        # Test health endpoint
        print("2. Testing Health Endpoint")
        self.test_endpoint("GET", "/health")
        
        # Test model info
        print("3. Testing Model Info")
        self.test_endpoint("GET", "/model-info")
        
        # Test media upload if test files exist
        print("4. Testing Media Upload")
        test_image = Path("../test-data/test_image.jpg")
        uploaded_asset_id = None
        
        if test_image.exists():
            with open(test_image, 'rb') as f:
                files = {'file': ('test_image.jpg', f, 'image/jpeg')}
                result = self.test_endpoint("POST", "/upload-media", files=files)
                if result["success"] and "response_data" in result:
                    uploaded_asset_id = result["response_data"].get("asset_id")
                    print(f"  Uploaded asset ID: {uploaded_asset_id}")
        else:
            print("  ⚠️ Test image not found, skipping upload test")
        
        # Test feature extraction if we have an asset
        if uploaded_asset_id:
            print("5. Testing Feature Extraction")
            self.test_endpoint("POST", "/extract-features", {"asset_id": uploaded_asset_id})
            
            print("6. Testing Quality Analysis")
            self.test_endpoint("POST", "/analyze-quality", {"asset_id": uploaded_asset_id})
            
            print("7. Testing Media Retrieval")
            self.test_endpoint("GET", f"/media/{uploaded_asset_id}")
        
        return True

    def generate_summary_report(self):
        """Generate a summary report of test results."""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - successful_tests
        
        report = f"""# DINOv3 Service Test Results

**Test Summary:**
- Total Tests: {total_tests}
- Successful: {successful_tests} ✓
- Failed: {failed_tests} ✗
- Success Rate: {(successful_tests/total_tests*100):.1f}%

**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Service URL:** {self.base_url}

---

## Test Results

| Endpoint | Method | Status | Duration (ms) | Notes |
|----------|--------|--------|---------------|-------|
"""
        
        for result in self.results:
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            error_note = f" - {result['error']}" if result["error"] else ""
            report += f"| {result['endpoint']} | {result['method']} | {status} | {result['duration_ms']} | HTTP {result['status_code']}{error_note} |\n"
        
        report += f"""
---

## Service Status

"""
        
        if successful_tests > 0:
            report += "✅ **Service is operational** - Basic endpoints are responding correctly.\n\n"
        else:
            report += "❌ **Service is not operational** - No endpoints are responding correctly.\n\n"
        
        if failed_tests > 0:
            report += f"⚠️ **{failed_tests} endpoints failed** - Check service logs for details.\n\n"
        
        # Add recommendations
        report += """## Recommendations

"""
        
        if any(r["error"] and "Connection refused" in r["error"] for r in self.results):
            report += "- Start the DINOv3 service: `python -m uvicorn app.main:app --host 0.0.0.0 --port 3012`\n"
        
        if any(r["status_code"] == 500 for r in self.results):
            report += "- Check service logs for internal server errors\n"
        
        if any(r["status_code"] == 404 for r in self.results):
            report += "- Verify endpoint URLs and API routing configuration\n"
        
        return report

def main():
    """Main test execution."""
    tester = SimpleEndpointTester()
    
    # Run basic tests
    service_available = tester.run_basic_tests()
    
    # Generate and save report
    report = tester.generate_summary_report()
    
    # Save to service-test-results.md
    report_path = Path("../service-test-results.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 50)
    print("TEST EXECUTION COMPLETED")
    print("=" * 50)
    print(f"Report saved to: {report_path.absolute()}")
    
    # Print summary
    total = len(tester.results)
    successful = len([r for r in tester.results if r["success"]])
    print(f"Results: {successful}/{total} tests passed ({(successful/total*100):.1f}%)")
    
    if not service_available:
        print("\n⚠️ Service is not running. Please start it and run tests again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
