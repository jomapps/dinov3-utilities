#!/usr/bin/env python3
"""
Investigate upload-media endpoint issues with real test data.
"""

import requests
import json
from pathlib import Path

def test_upload_with_test_data():
    """Test upload endpoint with actual test data."""
    
    print("=== UPLOAD-MEDIA ENDPOINT INVESTIGATION ===")
    print(f"Testing with image from test-data folder")
    
    # Check if test image exists
    test_image_path = Path("test-data/test_image.jpg")
    if not test_image_path.exists():
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print(f"✅ Found test image: {test_image_path}")
    print(f"   File size: {test_image_path.stat().st_size} bytes")
    
    # Test the upload endpoint
    url = "http://localhost:3012/api/v1/upload-media"
    
    try:
        # Test 1: Basic upload
        print(f"\n--- Test 1: Basic Upload ---")
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print("❌ Upload failed!")
            print(f"Response Text: {response.text}")
            
            # Try to parse as JSON for more details
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                pass
    
    except Exception as e:
        print(f"❌ Request failed with exception: {e}")
    
    # Test 2: Different content types
    print(f"\n--- Test 2: Different Content Types ---")
    content_types = [
        'image/jpeg',
        'image/jpg', 
        'application/octet-stream',
        None  # Let requests auto-detect
    ]
    
    for content_type in content_types:
        try:
            print(f"\nTesting with content-type: {content_type}")
            with open(test_image_path, 'rb') as f:
                if content_type:
                    files = {'file': ('test_image.jpg', f, content_type)}
                else:
                    files = {'file': ('test_image.jpg', f)}
                response = requests.post(url, files=files)
            
            print(f"  Status: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:200]}")
        except Exception as e:
            print(f"  Exception: {e}")
    
    # Test 3: Check service health
    print(f"\n--- Test 3: Service Health Check ---")
    try:
        health_response = requests.get("http://localhost:3012/api/v1/health")
        print(f"Health Status: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Service Status: {health_data.get('status', 'unknown')}")
        else:
            print(f"Health check failed: {health_response.text}")
    except Exception as e:
        print(f"Health check exception: {e}")
    
    # Test 4: Check if service is actually running
    print(f"\n--- Test 4: Service Process Check ---")
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        uvicorn_processes = [line for line in result.stdout.split('\n') if 'uvicorn' in line and '3012' in line]
        if uvicorn_processes:
            print("✅ Service is running:")
            for process in uvicorn_processes:
                print(f"  {process}")
        else:
            print("❌ No uvicorn process found on port 3012")
    except Exception as e:
        print(f"Process check failed: {e}")

if __name__ == "__main__":
    test_upload_with_test_data()
