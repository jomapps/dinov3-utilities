#!/usr/bin/env python3
"""
Test upload-media endpoint with various edge cases that might cause bad requests.
"""

import requests
import json
from pathlib import Path
import mimetypes

def test_upload_edge_cases():
    """Test various scenarios that might cause upload failures."""
    
    print("=== UPLOAD-MEDIA EDGE CASE TESTING ===")
    
    test_image_path = Path("test-data/test_image.jpg")
    if not test_image_path.exists():
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    url = "http://localhost:3012/api/v1/upload-media"
    
    # Test cases that might cause bad requests
    test_cases = [
        {
            "name": "Normal upload with explicit content-type",
            "files": lambda f: {'file': ('test.jpg', f, 'image/jpeg')},
            "expected": 200
        },
        {
            "name": "Upload without content-type (auto-detect)",
            "files": lambda f: {'file': ('test.jpg', f)},
            "expected": 400  # This might fail due to strict validation
        },
        {
            "name": "Upload with wrong content-type",
            "files": lambda f: {'file': ('test.jpg', f, 'text/plain')},
            "expected": 400
        },
        {
            "name": "Upload with generic content-type",
            "files": lambda f: {'file': ('test.jpg', f, 'application/octet-stream')},
            "expected": 400  # This might fail due to strict validation
        },
        {
            "name": "Upload with filename without extension",
            "files": lambda f: {'file': ('test', f, 'image/jpeg')},
            "expected": 200
        },
        {
            "name": "Upload with different image extensions",
            "files": lambda f: {'file': ('test.png', f, 'image/jpeg')},
            "expected": 200
        },
        {
            "name": "Upload with empty filename",
            "files": lambda f: {'file': ('', f, 'image/jpeg')},
            "expected": 200  # Should work if content-type is correct
        },
        {
            "name": "Upload with None content-type",
            "files": lambda f: {'file': ('test.jpg', f, None)},
            "expected": 400
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        
        try:
            with open(test_image_path, 'rb') as f:
                files = test_case['files'](f)
                response = requests.post(url, files=files)
            
            print(f"Status Code: {response.status_code} (expected: {test_case['expected']})")
            
            if response.status_code == test_case['expected']:
                print("✅ Result matches expectation")
                status = "PASS"
            else:
                print("❌ Result differs from expectation")
                status = "FAIL"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Asset ID: {data.get('asset_id', 'N/A')}")
                    print(f"File Size: {data.get('file_size', 'N/A')} bytes")
                except:
                    print("Could not parse response JSON")
            else:
                print(f"Error: {response.text[:200]}")
            
            results.append({
                "test": test_case['name'],
                "status_code": response.status_code,
                "expected": test_case['expected'],
                "status": status,
                "response": response.text[:100] if response.status_code != 200 else "Success"
            })
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "test": test_case['name'],
                "status_code": "ERROR",
                "expected": test_case['expected'],
                "status": "ERROR",
                "response": str(e)
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    print(f"\nDetailed Results:")
    for result in results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_icon} {result['test']}")
        print(f"   Status: {result['status_code']} (expected: {result['expected']})")
        if result['status'] != 'PASS':
            print(f"   Response: {result['response']}")
    
    # Identify the most likely cause of "bad request" errors
    print(f"\n{'='*60}")
    print("ANALYSIS")
    print(f"{'='*60}")
    
    content_type_failures = [r for r in results if 'content-type' in r['response'].lower() or r['status_code'] == 400]
    if content_type_failures:
        print("🔍 Content-type validation appears to be the main issue:")
        print("   - Files without explicit 'image/*' content-type are rejected")
        print("   - This is too strict and causes legitimate uploads to fail")
        print("   - Recommendation: Improve content-type detection logic")
    
    print(f"\n💡 To fix 'bad request' errors:")
    print("   1. Always specify content-type as 'image/jpeg', 'image/png', etc.")
    print("   2. Or improve the server-side content-type validation")

if __name__ == "__main__":
    test_upload_edge_cases()
