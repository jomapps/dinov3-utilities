#!/usr/bin/env python3
"""
Quick production service test to check current status
"""
import requests
import json
from datetime import datetime
import sys

# Production service URL
BASE_URL = "https://dino.ft.tc"
API_BASE = f"{BASE_URL}/api/v1"

def test_endpoint(method, url, data=None):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        status = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
        print(f"{status} {method} {url} - HTTP {response.status_code}")
        
        if response.status_code == 200:
            try:
                return {"status": "PASS", "data": response.json()}
            except:
                return {"status": "PASS", "data": response.text}
        else:
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
                return {"status": "FAIL", "error": error_data}
            except:
                print(f"  Error: {response.text}")
                return {"status": "FAIL", "error": response.text}
                
    except Exception as e:
        print(f"✗ ERROR {method} {url} - {str(e)}")
        return {"status": "ERROR", "error": str(e)}

def main():
    print("Testing DINOv3 Production Service")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    results = []
    
    # Test basic endpoints
    print("\n1. Testing Service Availability")
    results.append(test_endpoint("GET", BASE_URL))
    
    print("\n2. Testing Health Endpoint")
    health_result = test_endpoint("GET", f"{API_BASE}/health")
    results.append(health_result)
    
    print("\n3. Testing Model Info")
    results.append(test_endpoint("GET", f"{API_BASE}/model-info"))
    
    print("\n4. Testing Configuration")
    config_result = test_endpoint("GET", f"{API_BASE}/config")
    results.append(config_result)
    
    print("\n5. Testing Shot Library")
    results.append(test_endpoint("GET", f"{API_BASE}/shot-library"))
    
    print("\n6. Testing Documentation")
    results.append(test_endpoint("GET", f"{BASE_URL}/docs"))
    results.append(test_endpoint("GET", f"{BASE_URL}/openapi.json"))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["status"] == "PASS")
    failed_tests = sum(1 for r in results if r["status"] == "FAIL")
    error_tests = sum(1 for r in results if r["status"] == "ERROR")
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✓")
    print(f"Failed: {failed_tests} ✗")
    print(f"Errors: {error_tests} ⚠️")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    # Show health details if available
    if health_result["status"] == "PASS" and "data" in health_result:
        print("\n" + "=" * 60)
        print("HEALTH DETAILS")
        print("=" * 60)
        health_data = health_result["data"]
        print(json.dumps(health_data, indent=2))
    
    # Show config details if available
    if config_result["status"] == "PASS" and "data" in config_result:
        print("\n" + "=" * 60)
        print("CONFIGURATION")
        print("=" * 60)
        config_data = config_result["data"]
        print(json.dumps(config_data, indent=2))
    
    return passed_tests, failed_tests, error_tests

if __name__ == "__main__":
    passed, failed, errors = main()
    sys.exit(0 if failed == 0 and errors == 0 else 1)
