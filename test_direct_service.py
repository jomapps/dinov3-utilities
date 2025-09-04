#!/usr/bin/env python3
"""
Direct test of the DINOv3 service to verify it's working correctly.
"""

import asyncio
import requests
import json

async def test_service_directly():
    """Test the service directly to see what's happening."""
    
    # Test basic endpoints first
    print("Testing basic endpoints...")
    
    try:
        response = requests.get("http://localhost:3012/api/v1/health")
        print(f"Health endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health endpoint failed: {e}")
    
    try:
        response = requests.get("http://localhost:3012/api/v1/model-info")
        print(f"Model info endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Model info endpoint failed: {e}")
    
    # Test upload
    print("\nTesting upload...")
    try:
        with open("test_image.jpg", "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            response = requests.post("http://localhost:3012/api/v1/upload-media", files=files)
            print(f"Upload response: {response.status_code}")
            if response.status_code == 200:
                upload_data = response.json()
                asset_id = upload_data.get("asset_id")
                print(f"Uploaded asset ID: {asset_id}")
                
                # Test feature extraction with different approaches
                print(f"\nTesting feature extraction for asset: {asset_id}")
                
                # Try as query parameter
                response = requests.post(f"http://localhost:3012/api/v1/extract-features?asset_id={asset_id}")
                print(f"Feature extraction (query param): {response.status_code}")
                if response.status_code != 200:
                    print(f"Error response: {response.text}")
                
                # Try as JSON body
                response = requests.post("http://localhost:3012/api/v1/extract-features", 
                                       json={"asset_id": asset_id})
                print(f"Feature extraction (JSON body): {response.status_code}")
                if response.status_code != 200:
                    print(f"Error response: {response.text}")
                
                # Try as form data
                response = requests.post("http://localhost:3012/api/v1/extract-features", 
                                       data={"asset_id": asset_id})
                print(f"Feature extraction (form data): {response.status_code}")
                if response.status_code != 200:
                    print(f"Error response: {response.text}")
                
            else:
                print(f"Upload failed: {response.text}")
    except Exception as e:
        print(f"Upload test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_service_directly())
