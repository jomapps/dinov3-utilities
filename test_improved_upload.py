#!/usr/bin/env python3
"""
Test the improved upload-media endpoint with better content-type detection.
"""

import requests
import json
from pathlib import Path

def test_improved_upload():
    """Test the improved upload endpoint."""
    
    print("=== TESTING IMPROVED UPLOAD-MEDIA ENDPOINT ===")
    
    test_image_path = Path("test-data/test_image.jpg")
    if not test_image_path.exists():
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    url = "http://localhost:3012/api/v1/upload-media"
    
    # Test cases that should now work better
    test_cases = [
        {
            "name": "✅ Normal upload with explicit image/jpeg",
            "files": lambda f: {'file': ('test.jpg', f, 'image/jpeg')},
            "should_work": True
        },
        {
            "name": "✅ Upload with image/png content-type (JPEG file)",
            "files": lambda f: {'file': ('test.jpg', f, 'image/png')},
            "should_work": True  # Content-type mismatch but valid image
        },
        {
            "name": "✅ Upload without content-type but with .jpg extension",
            "files": lambda f: {'file': ('test.jpg', f)},
            "should_work": True  # Should now work with improved detection
        },
        {
            "name": "✅ Upload with application/octet-stream but .jpg extension",
            "files": lambda f: {'file': ('test.jpg', f, 'application/octet-stream')},
            "should_work": True  # Should now work with improved detection
        },
        {
            "name": "✅ Upload with .jpeg extension",
            "files": lambda f: {'file': ('test.jpeg', f, 'application/octet-stream')},
            "should_work": True
        },
        {
            "name": "✅ Upload with .png extension (JPEG content)",
            "files": lambda f: {'file': ('test.png', f, 'application/octet-stream')},
            "should_work": True
        },
        {
            "name": "❌ Upload with no extension and no image content-type",
            "files": lambda f: {'file': ('test', f, 'application/octet-stream')},
            "should_work": False  # Should still fail - no way to detect it's an image
        },
        {
            "name": "❌ Upload with text content-type and no image extension",
            "files": lambda f: {'file': ('test.txt', f, 'text/plain')},
            "should_work": False  # Should fail
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        
        try:
            with open(test_image_path, 'rb') as f:
                files = test_case['files'](f)
                response = requests.post(url, files=files)
            
            success = response.status_code == 200
            expected_success = test_case['should_work']
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected to work: {expected_success}")
            print(f"Actually worked: {success}")
            
            if success == expected_success:
                print("✅ Result matches expectation")
                status = "PASS"
            else:
                print("❌ Result differs from expectation")
                status = "FAIL"
            
            if success:
                try:
                    data = response.json()
                    print(f"Asset ID: {data.get('asset_id', 'N/A')}")
                    print(f"Content Type: {data.get('content_type', 'N/A')}")
                    print(f"File Size: {data.get('file_size', 'N/A')} bytes")
                    print(f"Dimensions: {data.get('width', 'N/A')}x{data.get('height', 'N/A')}")
                except:
                    print("Could not parse response JSON")
            else:
                print(f"Error: {response.text}")
            
            results.append({
                "test": test_case['name'],
                "status_code": response.status_code,
                "expected_success": expected_success,
                "actual_success": success,
                "status": status
            })
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "test": test_case['name'],
                "status_code": "ERROR",
                "expected_success": test_case['should_work'],
                "actual_success": False,
                "status": "ERROR"
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("IMPROVED UPLOAD TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for result in results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_icon} {result['test']}")
        if result['status'] != 'PASS':
            print(f"   Expected: {'Success' if result['expected_success'] else 'Failure'}")
            print(f"   Got: {'Success' if result['actual_success'] else 'Failure'}")
    
    # Check improvement
    improved_cases = [r for r in results if "without content-type" in r['test'] or "application/octet-stream" in r['test']]
    improved_working = sum(1 for r in improved_cases if r['actual_success'] and r['expected_success'])
    
    print(f"\n{'='*60}")
    print("IMPROVEMENT ANALYSIS")
    print(f"{'='*60}")
    
    if improved_working > 0:
        print(f"🎉 SUCCESS: {improved_working} previously failing cases now work!")
        print("   - Files without explicit image content-type now accepted")
        print("   - Generic content-types with image extensions now work")
        print("   - More robust content-type detection implemented")
    else:
        print("⚠️  No improvement detected - may need further fixes")
    
    print(f"\n💡 Upload Guidelines:")
    print("   ✅ Best: Use explicit image content-types (image/jpeg, image/png)")
    print("   ✅ Good: Use proper file extensions (.jpg, .jpeg, .png, etc.)")
    print("   ✅ OK: Generic content-types with image extensions work now")
    print("   ❌ Avoid: No content-type AND no image extension")

if __name__ == "__main__":
    test_improved_upload()
