"""
Comprehensive test suite for all DINOv3 service endpoints.
Tests each endpoint systematically and generates detailed results.
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
from datetime import datetime

class DINOv3EndpointTester:
    def __init__(self, base_url: str = "http://localhost:3012"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_results = []
        self.uploaded_assets = {}  # Store uploaded asset IDs for reuse
        
        # Test data paths
        self.test_image_path = Path("../test-data/test_image.jpg")
        self.test_video_path = Path("../test-data/test-video.mp4")
        
    async def log_result(self, endpoint: str, method: str, status: str, 
                        response_data: Any = None, error: str = None, 
                        duration: float = 0):
        """Log test result for later reporting."""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error": error
        }
        self.test_results.append(result)
        print(f"{'✓' if status == 'PASS' else '✗'} {method} {endpoint} - {status} ({result['duration_ms']}ms)")
        if error:
            print(f"  Error: {error}")

    async def test_endpoint(self, session: aiohttp.ClientSession, method: str, 
                           endpoint: str, data: Any = None, files: Any = None) -> Dict:
        """Test a single endpoint and return result."""
        url = f"{self.api_base}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with session.get(url) as response:
                    response_data = await response.json()
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        await self.log_result(endpoint, method, "PASS", response_data, duration=duration)
                        return {"status": "PASS", "data": response_data}
                    else:
                        await self.log_result(endpoint, method, "FAIL", response_data, 
                                            f"HTTP {response.status}", duration)
                        return {"status": "FAIL", "error": f"HTTP {response.status}"}
                        
            elif method.upper() == "POST":
                if files:
                    # Multipart form data
                    form_data = aiohttp.FormData()
                    for key, value in files.items():
                        if isinstance(value, tuple):  # (filename, file_content, content_type)
                            form_data.add_field(key, value[1], filename=value[0], content_type=value[2])
                        else:
                            form_data.add_field(key, value)
                    
                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, str(value))
                    
                    async with session.post(url, data=form_data) as response:
                        response_data = await response.json()
                        duration = time.time() - start_time
                        
                        if response.status in [200, 201]:
                            await self.log_result(endpoint, method, "PASS", response_data, duration=duration)
                            return {"status": "PASS", "data": response_data}
                        else:
                            await self.log_result(endpoint, method, "FAIL", response_data,
                                                f"HTTP {response.status}", duration)
                            return {"status": "FAIL", "error": f"HTTP {response.status}"}
                else:
                    # JSON data
                    headers = {"Content-Type": "application/json"}
                    async with session.post(url, json=data, headers=headers) as response:
                        response_data = await response.json()
                        duration = time.time() - start_time
                        
                        if response.status in [200, 201]:
                            await self.log_result(endpoint, method, "PASS", response_data, duration=duration)
                            return {"status": "PASS", "data": response_data}
                        else:
                            await self.log_result(endpoint, method, "FAIL", response_data,
                                                f"HTTP {response.status}", duration)
                            return {"status": "FAIL", "error": f"HTTP {response.status}"}
                            
            elif method.upper() == "PUT":
                headers = {"Content-Type": "application/json"}
                async with session.put(url, json=data, headers=headers) as response:
                    response_data = await response.json()
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        await self.log_result(endpoint, method, "PASS", response_data, duration=duration)
                        return {"status": "PASS", "data": response_data}
                    else:
                        await self.log_result(endpoint, method, "FAIL", response_data,
                                            f"HTTP {response.status}", duration)
                        return {"status": "FAIL", "error": f"HTTP {response.status}"}
                        
            elif method.upper() == "DELETE":
                async with session.delete(url) as response:
                    response_data = await response.json()
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        await self.log_result(endpoint, method, "PASS", response_data, duration=duration)
                        return {"status": "PASS", "data": response_data}
                    else:
                        await self.log_result(endpoint, method, "FAIL", response_data,
                                            f"HTTP {response.status}", duration)
                        return {"status": "FAIL", "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            duration = time.time() - start_time
            await self.log_result(endpoint, method, "ERROR", error=str(e), duration=duration)
            return {"status": "ERROR", "error": str(e)}

    async def upload_test_assets(self, session: aiohttp.ClientSession):
        """Upload test image and video for use in other tests."""
        print("\n=== Uploading Test Assets ===")
        
        # Upload test image
        if self.test_image_path.exists():
            with open(self.test_image_path, 'rb') as f:
                image_content = f.read()
            
            files = {
                'file': ('test_image.jpg', image_content, 'image/jpeg')
            }
            
            result = await self.test_endpoint(session, "POST", "/upload-media", files=files)
            if result["status"] == "PASS":
                self.uploaded_assets["test_image"] = result["data"]["asset_id"]
                print(f"  Uploaded test image: {self.uploaded_assets['test_image']}")
        
        # Upload test video
        if self.test_video_path.exists():
            with open(self.test_video_path, 'rb') as f:
                video_content = f.read()
            
            files = {
                'file': ('test-video.mp4', video_content, 'video/mp4')
            }
            
            result = await self.test_endpoint(session, "POST", "/upload-media", files=files)
            if result["status"] == "PASS":
                self.uploaded_assets["test_video"] = result["data"]["asset_id"]
                print(f"  Uploaded test video: {self.uploaded_assets['test_video']}")

    async def test_all_endpoints(self):
        """Test all DINOv3 service endpoints systematically."""
        print("Starting comprehensive DINOv3 endpoint testing...")
        print(f"Base URL: {self.base_url}")
        print(f"API Base: {self.api_base}")
        
        async with aiohttp.ClientSession() as session:
            # Test service availability first
            print("\n=== Testing Service Availability ===")
            await self.test_endpoint(session, "GET", "")  # Root endpoint
            
            # Upload test assets first
            await self.upload_test_assets(session)
            
            # 1. Utility Endpoints
            print("\n=== Testing Utility Endpoints ===")
            await self.test_endpoint(session, "GET", "/health")
            await self.test_endpoint(session, "GET", "/model-info")
            
            if "test_image" in self.uploaded_assets:
                await self.test_endpoint(session, "POST", "/preprocess-image", 
                                       {"asset_id": self.uploaded_assets["test_image"]})
            
            # 2. Media Asset Management
            print("\n=== Testing Media Asset Management ===")
            if "test_image" in self.uploaded_assets:
                asset_id = self.uploaded_assets["test_image"]
                await self.test_endpoint(session, "GET", f"/media/{asset_id}")
                # Note: We'll test DELETE at the end to avoid breaking other tests
            
            # 3. Core Feature Extraction
            print("\n=== Testing Feature Extraction ===")
            if "test_image" in self.uploaded_assets:
                await self.test_endpoint(session, "POST", "/extract-features",
                                       {"asset_id": self.uploaded_assets["test_image"]})
            
            # 4. Image Similarity & Matching
            print("\n=== Testing Similarity & Matching ===")
            if "test_image" in self.uploaded_assets:
                asset_id = self.uploaded_assets["test_image"]
                
                # Upload a second copy for comparison
                if self.test_image_path.exists():
                    with open(self.test_image_path, 'rb') as f:
                        image_content = f.read()
                    files = {'file': ('test_image_2.jpg', image_content, 'image/jpeg')}
                    result = await self.test_endpoint(session, "POST", "/upload-media", files=files)
                    if result["status"] == "PASS":
                        asset_id_2 = result["data"]["asset_id"]
                        self.uploaded_assets["test_image_2"] = asset_id_2
                        
                        # Test similarity endpoints
                        await self.test_endpoint(session, "POST", "/calculate-similarity",
                                               {"asset_id_1": asset_id, "asset_id_2": asset_id_2})
                        
                        await self.test_endpoint(session, "POST", "/find-best-match",
                                               {"reference_asset_id": asset_id, 
                                                "candidate_asset_ids": [asset_id_2]})
                        
                        await self.test_endpoint(session, "POST", "/validate-consistency",
                                               {"asset_id_1": asset_id, "asset_id_2": asset_id_2})
            
            # 5. Quality Analysis
            print("\n=== Testing Quality Analysis ===")
            if "test_image" in self.uploaded_assets:
                asset_id = self.uploaded_assets["test_image"]
                await self.test_endpoint(session, "POST", "/analyze-quality",
                                       {"asset_id": asset_id})
                await self.test_endpoint(session, "POST", "/analyze-image-metrics",
                                       {"asset_id": asset_id})
            
            # 6. Batch Processing
            print("\n=== Testing Batch Processing ===")
            if len(self.uploaded_assets) >= 2:
                asset_ids = list(self.uploaded_assets.values())[:2]
                await self.test_endpoint(session, "POST", "/batch-similarity",
                                       {"asset_ids": asset_ids})
                await self.test_endpoint(session, "POST", "/batch-quality-check",
                                       {"asset_ids": asset_ids})
            
            # 7. Character/Person Analysis
            print("\n=== Testing Character Analysis ===")
            if "test_image" in self.uploaded_assets and "test_image_2" in self.uploaded_assets:
                ref_id = self.uploaded_assets["test_image"]
                test_ids = [self.uploaded_assets["test_image_2"]]
                
                await self.test_endpoint(session, "POST", "/character-matching",
                                       {"reference_asset_id": ref_id, "test_asset_ids": test_ids})
                
                await self.test_endpoint(session, "POST", "/group-by-character",
                                       {"asset_ids": [ref_id] + test_ids})
            
            # 8. Production & Cinematic Services
            print("\n=== Testing Production Services ===")
            if "test_image" in self.uploaded_assets and "test_image_2" in self.uploaded_assets:
                ref_id = self.uploaded_assets["test_image"]
                shot_ids = [self.uploaded_assets["test_image_2"]]
                
                await self.test_endpoint(session, "POST", "/validate-shot-consistency",
                                       {"character_reference_id": ref_id, "shot_asset_ids": shot_ids})
                
                await self.test_endpoint(session, "POST", "/reference-enforcement",
                                       {"master_reference_id": ref_id, "generated_asset_ids": shot_ids})
            
            # 9. Video Shot Analysis
            print("\n=== Testing Video Analysis ===")
            if "test_video" in self.uploaded_assets:
                video_id = self.uploaded_assets["test_video"]
                
                # Analyze video shots
                result = await self.test_endpoint(session, "POST", "/analyze-video-shots",
                                                {"asset_id": video_id})
                
                if result["status"] == "PASS" and "shots" in result["data"]:
                    shots_data = result["data"]["shots"]
                    
                    # Store shot data
                    await self.test_endpoint(session, "POST", "/store-shot-data",
                                           {"shot_data": shots_data, "scene_context": "Test scene"})
                    
                    # Get shot suggestions
                    await self.test_endpoint(session, "POST", "/suggest-shots",
                                           {"scene_description": "Test scene", "emotional_tone": "neutral"})
                    
                    # Browse shot library
                    await self.test_endpoint(session, "GET", "/shot-library")
            
            # 10. Advanced Analytics
            print("\n=== Testing Advanced Analytics ===")
            if len(self.uploaded_assets) >= 2:
                asset_ids = list(self.uploaded_assets.values())
                query_id = asset_ids[0]
                dataset_ids = asset_ids[1:]
                
                await self.test_endpoint(session, "POST", "/semantic-search",
                                       {"query_asset_id": query_id, "dataset_asset_ids": dataset_ids})
                
                await self.test_endpoint(session, "POST", "/anomaly-detection",
                                       {"reference_asset_ids": [query_id], "test_asset_ids": dataset_ids})
                
                await self.test_endpoint(session, "POST", "/feature-clustering",
                                       {"asset_ids": asset_ids, "n_clusters": 2})
            
            # 11. Configuration Endpoints
            print("\n=== Testing Configuration ===")
            await self.test_endpoint(session, "PUT", "/config/quality-threshold",
                                   {"threshold": 0.75})
            await self.test_endpoint(session, "PUT", "/config/similarity-threshold",
                                   {"threshold": 80.0})
            
            # 12. Cleanup - Delete test assets (optional, at the end)
            print("\n=== Testing Asset Deletion ===")
            for asset_name, asset_id in self.uploaded_assets.items():
                await self.test_endpoint(session, "DELETE", f"/media/{asset_id}")

    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        report = f"""# DINOv3 Service Endpoint Test Results

**Test Summary:**
- Total Tests: {total_tests}
- Passed: {passed_tests} ✓
- Failed: {failed_tests} ✗
- Errors: {error_tests} ⚠️
- Success Rate: {(passed_tests/total_tests*100):.1f}%

**Test Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Detailed Results

"""
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            endpoint = result["endpoint"]
            if "/upload-media" in endpoint or "/media/" in endpoint:
                category = "Media Management"
            elif "/extract-features" in endpoint or "/preprocess-image" in endpoint:
                category = "Feature Extraction"
            elif "/similarity" in endpoint or "/find-best-match" in endpoint or "/validate-consistency" in endpoint:
                category = "Similarity & Matching"
            elif "/quality" in endpoint or "/analyze-image-metrics" in endpoint:
                category = "Quality Analysis"
            elif "/batch-" in endpoint:
                category = "Batch Processing"
            elif "/character-" in endpoint or "/group-by-character" in endpoint:
                category = "Character Analysis"
            elif "/validate-shot" in endpoint or "/reference-enforcement" in endpoint:
                category = "Production Services"
            elif "/video" in endpoint or "/shot" in endpoint:
                category = "Video Analysis"
            elif "/semantic-search" in endpoint or "/anomaly-detection" in endpoint or "/clustering" in endpoint:
                category = "Advanced Analytics"
            elif "/config/" in endpoint:
                category = "Configuration"
            elif "/health" in endpoint or "/model-info" in endpoint:
                category = "Utilities"
            else:
                category = "Other"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        for category, results in categories.items():
            report += f"### {category}\n\n"
            for result in results:
                status_icon = "✓" if result["status"] == "PASS" else ("✗" if result["status"] == "FAIL" else "⚠️")
                report += f"- {status_icon} **{result['method']} {result['endpoint']}** - {result['status']} ({result['duration_ms']}ms)\n"
                if result["error"]:
                    report += f"  - Error: {result['error']}\n"
                report += "\n"
        
        return report

async def main():
    """Main test execution function."""
    tester = DINOv3EndpointTester()
    
    try:
        await tester.test_all_endpoints()
        
        # Generate and save report
        report = tester.generate_report()
        
        # Save to service-test-results.md
        report_path = Path("../service-test-results.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n{'='*60}")
        print("TEST EXECUTION COMPLETED")
        print(f"{'='*60}")
        print(f"Report saved to: {report_path.absolute()}")
        print(f"Total tests: {len(tester.test_results)}")
        print(f"Passed: {len([r for r in tester.test_results if r['status'] == 'PASS'])}")
        print(f"Failed: {len([r for r in tester.test_results if r['status'] == 'FAIL'])}")
        print(f"Errors: {len([r for r in tester.test_results if r['status'] == 'ERROR'])}")
        
    except Exception as e:
        print(f"Test execution failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
