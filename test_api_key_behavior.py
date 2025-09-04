#!/usr/bin/env python3
"""
Test what happens when API keys are sent to the current service.
"""

import requests
import json
from pathlib import Path

def test_api_key_behavior():
    """Test various API key scenarios with the current service."""
    
    print("=== TESTING API KEY BEHAVIOR ===")
    print("Testing what happens when API keys are sent to the current service...")
    
    test_image_path = Path("test-data/test_image.jpg")
    if not test_image_path.exists():
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    base_url = "http://localhost:3012/api/v1"
    
    # Test scenarios with different API key formats
    test_scenarios = [
        {
            "name": "No API Key (baseline)",
            "headers": {},
            "expected": "Should work normally"
        },
        {
            "name": "X-API-Key header",
            "headers": {"X-API-Key": "test-api-key-12345"},
            "expected": "Should be ignored"
        },
        {
            "name": "Authorization Bearer",
            "headers": {"Authorization": "Bearer test-token-12345"},
            "expected": "Should be ignored"
        },
        {
            "name": "Authorization API Key",
            "headers": {"Authorization": "ApiKey test-key-12345"},
            "expected": "Should be ignored"
        },
        {
            "name": "Custom API-Key header",
            "headers": {"API-Key": "custom-key-12345"},
            "expected": "Should be ignored"
        },
        {
            "name": "Multiple auth headers",
            "headers": {
                "X-API-Key": "test-key-1",
                "Authorization": "Bearer test-token-2",
                "API-Key": "test-key-3"
            },
            "expected": "Should be ignored"
        },
        {
            "name": "Invalid header format",
            "headers": {"X-API-Key": ""},
            "expected": "Should be ignored"
        }
    ]
    
    results = []
    
    # Test health endpoint first (simple GET)
    print(f"\n=== Testing Health Endpoint ===")
    for scenario in test_scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        try:
            response = requests.get(f"{base_url}/health", headers=scenario['headers'])
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected: {scenario['expected']}")
            
            if response.status_code == 200:
                print("✅ Request successful - API key ignored")
                status = "IGNORED"
            else:
                print(f"❌ Request failed - Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                status = "ERROR"
            
            results.append({
                "endpoint": "/health",
                "scenario": scenario['name'],
                "status_code": response.status_code,
                "status": status,
                "headers": scenario['headers']
            })
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "endpoint": "/health",
                "scenario": scenario['name'],
                "status_code": "ERROR",
                "status": "EXCEPTION",
                "headers": scenario['headers']
            })
    
    # Test upload endpoint (POST with file)
    print(f"\n=== Testing Upload Endpoint ===")
    for scenario in test_scenarios[:3]:  # Test fewer scenarios for upload to save time
        print(f"\n--- {scenario['name']} ---")
        
        try:
            with open(test_image_path, 'rb') as f:
                files = {'file': ('test.jpg', f, 'image/jpeg')}
                response = requests.post(f"{base_url}/upload-media", 
                                       files=files, 
                                       headers=scenario['headers'])
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected: {scenario['expected']}")
            
            if response.status_code == 200:
                print("✅ Upload successful - API key ignored")
                data = response.json()
                print(f"Asset ID: {data.get('asset_id', 'N/A')}")
                status = "IGNORED"
            else:
                print(f"❌ Upload failed - Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                status = "ERROR"
            
            results.append({
                "endpoint": "/upload-media",
                "scenario": scenario['name'],
                "status_code": response.status_code,
                "status": status,
                "headers": scenario['headers']
            })
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "endpoint": "/upload-media",
                "scenario": scenario['name'],
                "status_code": "ERROR",
                "status": "EXCEPTION",
                "headers": scenario['headers']
            })
    
    # Test with query parameters (another common API key method)
    print(f"\n=== Testing Query Parameter API Keys ===")
    query_scenarios = [
        {
            "name": "API key as query param",
            "url": f"{base_url}/health?api_key=test-key-12345",
            "expected": "Should be ignored"
        },
        {
            "name": "Token as query param", 
            "url": f"{base_url}/health?token=test-token-12345",
            "expected": "Should be ignored"
        },
        {
            "name": "Key as query param",
            "url": f"{base_url}/health?key=test-key-12345", 
            "expected": "Should be ignored"
        }
    ]
    
    for scenario in query_scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        try:
            response = requests.get(scenario['url'])
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected: {scenario['expected']}")
            
            if response.status_code == 200:
                print("✅ Request successful - Query param ignored")
                status = "IGNORED"
            else:
                print(f"❌ Request failed - Status: {response.status_code}")
                status = "ERROR"
            
            results.append({
                "endpoint": "/health",
                "scenario": scenario['name'],
                "status_code": response.status_code,
                "status": status,
                "url": scenario['url']
            })
            
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("API KEY BEHAVIOR SUMMARY")
    print(f"{'='*60}")
    
    ignored_count = sum(1 for r in results if r['status'] == 'IGNORED')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    total_count = len(results)
    
    print(f"Total Tests: {total_count}")
    print(f"API Keys Ignored: {ignored_count}")
    print(f"Errors Caused: {error_count}")
    
    if error_count == 0:
        print(f"\n✅ RESULT: API keys are SAFELY IGNORED")
        print("   - No errors caused by sending API keys")
        print("   - Service accepts requests with or without API keys")
        print("   - Headers and query parameters are ignored")
    else:
        print(f"\n⚠️ RESULT: Some API key formats cause ERRORS")
        print("   - Check specific scenarios that failed")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result['status'] == 'IGNORED' else "❌"
        print(f"{status_icon} {result['endpoint']} - {result['scenario']}: {result['status']}")
    
    print(f"\n💡 CONCLUSION:")
    if error_count == 0:
        print("   External apps can safely send API keys - they will be ignored")
        print("   No breaking changes if API key authentication is added later")
    else:
        print("   Some API key formats may cause issues")
        print("   Test thoroughly before implementing authentication")

if __name__ == "__main__":
    test_api_key_behavior()
