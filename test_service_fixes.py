#!/usr/bin/env python3
"""
Comprehensive test script to verify DINOv3 service fixes and functionality.
Tests all endpoints with real data to ensure everything works correctly.
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path
from PIL import Image
import io
import base64
import sys

class DINOv3ServiceTester:
    def __init__(self, base_url="http://localhost:3012"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_results = []
        self.uploaded_assets = {}
        
        # Create test image if it doesn't exist
        self.test_image_path = Path("test_image.jpg")
        self.create_test_image()
    
    def create_test_image(self):
        """Create a simple test image for upload testing."""
        if not self.test_image_path.exists():
            # Create a simple 256x256 RGB image with gradient
            img = Image.new('RGB', (256, 256))
            pixels = img.load()
            
            for i in range(256):
                for j in range(256):
                    pixels[i, j] = (i, j, (i + j) % 256)
            
            img.save(self.test_image_path, 'JPEG', quality=95)
            print(f"Created test image: {self.test_image_path}")
    
    async def test_endpoint(self, session, method, endpoint, **kwargs):
        """Test a single endpoint and return results."""
        url = f"{self.api_base}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                async with session.get(url, **kwargs) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    return {
                        "endpoint": endpoint,
                        "method": method,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": response.status < 400,
                        "data": data,
                        "error": None
                    }
            
            elif method == "POST":
                # Handle file uploads
                if 'files' in kwargs:
                    data = aiohttp.FormData()
                    files = kwargs.pop('files')
                    for key, (filename, content, content_type) in files.items():
                        data.add_field(key, content, filename=filename, content_type=content_type)
                    
                    async with session.post(url, data=data, **kwargs) as response:
                        response_time = time.time() - start_time
                        response_data = await response.json()
                        
                        return {
                            "endpoint": endpoint,
                            "method": method,
                            "status_code": response.status,
                            "response_time": response_time,
                            "success": response.status < 400,
                            "data": response_data,
                            "error": None
                        }
                else:
                    # Regular JSON POST
                    async with session.post(url, **kwargs) as response:
                        response_time = time.time() - start_time
                        response_data = await response.json()
                        
                        return {
                            "endpoint": endpoint,
                            "method": method,
                            "status_code": response.status,
                            "response_time": response_time,
                            "success": response.status < 400,
                            "data": response_data,
                            "error": None
                        }
        
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    async def test_basic_endpoints(self, session):
        """Test basic service endpoints."""
        print("\n=== Testing Basic Endpoints ===")
        
        endpoints = [
            ("GET", "/health"),
            ("GET", "/model-info"),
            ("GET", "/config"),
            ("GET", "/shot-library")
        ]
        
        for method, endpoint in endpoints:
            result = await self.test_endpoint(session, method, endpoint)
            self.test_results.append(result)
            
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            print(f"  {endpoint}: {status} ({result['response_time']:.3f}s)")
            
            if not result["success"]:
                print(f"    Error: {result.get('error', 'HTTP ' + str(result['status_code']))}")
    
    async def test_upload_media(self, session):
        """Test media upload functionality with real image."""
        print("\n=== Testing Media Upload ===")
        
        if not self.test_image_path.exists():
            print("  ✗ Test image not found, skipping upload test")
            return
        
        # Read test image
        with open(self.test_image_path, 'rb') as f:
            image_content = f.read()
        
        files = {
            'file': ('test_image.jpg', image_content, 'image/jpeg')
        }
        
        result = await self.test_endpoint(session, "POST", "/upload-media", files=files)
        self.test_results.append(result)
        
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        print(f"  /upload-media: {status} ({result['response_time']:.3f}s)")
        
        if result["success"]:
            asset_id = result["data"].get("asset_id")
            self.uploaded_assets["test_image"] = asset_id
            print(f"    Uploaded asset ID: {asset_id}")
            print(f"    File size: {result['data'].get('file_size')} bytes")
            print(f"    Public URL: {result['data'].get('public_url')}")
        else:
            print(f"    Error: {result.get('error', 'HTTP ' + str(result['status_code']))}")
            if result.get('data'):
                print(f"    Response: {result['data']}")
    
    async def test_feature_extraction(self, session):
        """Test feature extraction with uploaded asset."""
        print("\n=== Testing Feature Extraction ===")
        
        if "test_image" not in self.uploaded_assets:
            print("  ⚠️ No uploaded asset available, skipping feature extraction")
            return
        
        asset_id = self.uploaded_assets["test_image"]
        
        result = await self.test_endpoint(
            session, "POST", f"/extract-features?asset_id={asset_id}"
        )
        self.test_results.append(result)
        
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        print(f"  /extract-features: {status} ({result['response_time']:.3f}s)")
        
        if result["success"]:
            features = result["data"].get("features", [])
            print(f"    Features extracted: {len(features)} dimensions")
            print(f"    Processing time: {result['data'].get('processing_time', 0):.3f}s")
        else:
            print(f"    Error: {result.get('error', 'HTTP ' + str(result['status_code']))}")
            if result.get('data'):
                print(f"    Response: {result['data']}")
    
    async def test_quality_analysis(self, session):
        """Test quality analysis with uploaded asset."""
        print("\n=== Testing Quality Analysis ===")
        
        if "test_image" not in self.uploaded_assets:
            print("  ⚠️ No uploaded asset available, skipping quality analysis")
            return
        
        asset_id = self.uploaded_assets["test_image"]
        
        result = await self.test_endpoint(
            session, "POST", "/analyze-quality",
            json={"asset_id": asset_id}
        )
        self.test_results.append(result)
        
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        print(f"  /analyze-quality: {status} ({result['response_time']:.3f}s)")
        
        if result["success"]:
            quality_score = result["data"].get("quality_score", 0)
            diversity_score = result["data"].get("diversity_score", 0)
            print(f"    Quality score: {quality_score:.3f}")
            print(f"    Diversity score: {diversity_score:.3f}")
        else:
            print(f"    Error: {result.get('error', 'HTTP ' + str(result['status_code']))}")
            if result.get('data'):
                print(f"    Response: {result['data']}")
    
    async def run_comprehensive_test(self):
        """Run all tests comprehensively."""
        print("Starting comprehensive DINOv3 service testing...")
        print(f"Base URL: {self.base_url}")
        print(f"API Base: {self.api_base}")
        
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Test basic endpoints
            await self.test_basic_endpoints(session)
            
            # Test media upload
            await self.test_upload_media(session)
            
            # Test feature extraction
            await self.test_feature_extraction(session)
            
            # Test quality analysis
            await self.test_quality_analysis(session)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✓")
        print(f"Failed: {failed_tests} ✗")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['endpoint']} ({result['method']}): {result.get('error', 'HTTP ' + str(result['status_code']))}")
        
        print(f"\nTest completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Main test function."""
    tester = DINOv3ServiceTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
