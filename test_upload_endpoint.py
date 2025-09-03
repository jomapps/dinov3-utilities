#!/usr/bin/env python3
"""
Test the upload-media endpoint specifically
"""
import requests
import json
from pathlib import Path
from datetime import datetime

# Production service URL
BASE_URL = "https://dino.ft.tc"
API_BASE = f"{BASE_URL}/api/v1"

def test_upload_media():
    """Test the upload-media endpoint with test image"""
    print("Testing upload-media endpoint")
    print(f"URL: {API_BASE}/upload-media")
    print("=" * 50)
    
    # Check if test image exists
    test_image_path = Path("test-data/test_image.jpg")
    if not test_image_path.exists():
        test_image_path = Path("test_image.jpg")
    
    if not test_image_path.exists():
        print("❌ Test image not found. Looking for:")
        print(f"  - test-data/test_image.jpg")
        print(f"  - test_image.jpg")
        return False
    
    print(f"✓ Found test image: {test_image_path}")
    
    try:
        # Prepare multipart form data
        with open(test_image_path, 'rb') as f:
            files = {
                'file': ('test_image.jpg', f, 'image/jpeg')
            }
            
            print(f"\nUploading {test_image_path.name}...")
            response = requests.post(
                f"{API_BASE}/upload-media",
                files=files,
                timeout=60
            )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS - Upload completed!")
            try:
                result = response.json()
                print("Response Data:")
                print(json.dumps(result, indent=2))
                
                if 'asset_id' in result:
                    asset_id = result['asset_id']
                    print(f"\n🎯 Asset ID: {asset_id}")
                    
                    # Test retrieving the uploaded media
                    print(f"\nTesting media retrieval...")
                    get_response = requests.get(f"{API_BASE}/media/{asset_id}", timeout=30)
                    print(f"Media retrieval status: {get_response.status_code}")
                    
                    if get_response.status_code == 200:
                        print("✅ Media retrieval successful!")
                        try:
                            media_info = get_response.json()
                            print("Media Info:")
                            print(json.dumps(media_info, indent=2))
                        except:
                            print("Media info (non-JSON):", get_response.text[:200])
                    else:
                        print("❌ Media retrieval failed")
                        print("Error:", get_response.text[:200])
                
                return True
                
            except json.JSONDecodeError:
                print("✅ SUCCESS - Upload completed (non-JSON response)")
                print("Response:", response.text[:500])
                return True
                
        else:
            print("❌ FAILED - Upload failed")
            print("Error Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text[:500])
            return False
            
    except Exception as e:
        print(f"❌ ERROR - Exception occurred: {str(e)}")
        return False

def main():
    print("DINOv3 Upload-Media Endpoint Test")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    success = test_upload_media()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 UPLOAD TEST PASSED")
    else:
        print("💥 UPLOAD TEST FAILED")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
