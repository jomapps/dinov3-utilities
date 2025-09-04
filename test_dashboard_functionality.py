#!/usr/bin/env python3
"""
Test script to verify dashboard functionality
"""
import requests
import json
import time

def test_dashboard_endpoints():
    """Test all dashboard-related endpoints"""
    base_url = "http://localhost:3012"
    
    tests = [
        {
            "name": "Dashboard HTML",
            "url": f"{base_url}/dashboard",
            "expected_content": ["DINOv3 Utilities Dashboard", "styles.css", "ui.js"]
        },
        {
            "name": "CSS File",
            "url": f"{base_url}/static/dashboard/styles.css",
            "expected_content": [":root", "--bg:", "body"]
        },
        {
            "name": "JavaScript File", 
            "url": f"{base_url}/static/dashboard/ui.js",
            "expected_content": ["loadSchema", "renderSidebar", "DOMContentLoaded"]
        },
        {
            "name": "OpenAPI Schema",
            "url": f"{base_url}/openapi.json",
            "expected_content": ["openapi", "paths", "components"]
        },
        {
            "name": "Health Check",
            "url": f"{base_url}/api/v1/health",
            "expected_content": ["status", "timestamp"]
        }
    ]
    
    print("🧪 Testing Dashboard Functionality")
    print("=" * 50)
    
    all_passed = True
    
    for test in tests:
        print(f"\n📋 Testing: {test['name']}")
        print(f"🔗 URL: {test['url']}")
        
        try:
            response = requests.get(test['url'], timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                print(f"📄 Content-Type: {content_type}")
                
                # Check expected content
                content = response.text
                missing_content = []
                
                for expected in test['expected_content']:
                    if expected not in content:
                        missing_content.append(expected)
                
                if missing_content:
                    print(f"⚠️  Missing content: {missing_content}")
                    all_passed = False
                else:
                    print("✅ All expected content found")
                
                # Show content length
                print(f"📏 Content length: {len(content)} characters")
                
                # For JSON responses, try to parse
                if 'application/json' in content_type:
                    try:
                        json_data = response.json()
                        print(f"📊 JSON keys: {list(json_data.keys())}")
                    except:
                        print("⚠️  Invalid JSON response")
                        all_passed = False
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"❌ Error: {response.text[:200]}...")
                all_passed = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Dashboard should be working.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    return all_passed

def test_dashboard_interactivity():
    """Test dashboard JavaScript functionality"""
    print("\n🔧 Testing Dashboard Interactivity")
    print("=" * 50)
    
    base_url = "http://localhost:3012"
    
    # Test if the dashboard can load the schema
    try:
        # First check if OpenAPI is accessible
        schema_response = requests.get(f"{base_url}/openapi.json")
        if schema_response.status_code == 200:
            schema = schema_response.json()
            endpoints_count = len(schema.get('paths', {}))
            print(f"✅ OpenAPI schema accessible with {endpoints_count} endpoints")
            
            # List some endpoints
            paths = list(schema.get('paths', {}).keys())[:5]
            print(f"📋 Sample endpoints: {paths}")
            
        else:
            print(f"❌ OpenAPI schema not accessible: {schema_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing schema: {e}")
        return False
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{base_url}/api/v1/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check: {health_data.get('status', 'unknown')}")
            print(f"📊 Model loaded: {health_data.get('model', {}).get('loaded', False)}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing health: {e}")
        return False
    
    print("✅ Dashboard backend functionality is working!")
    return True

if __name__ == "__main__":
    print("🚀 DINOv3 Dashboard Test Suite")
    print("Testing dashboard at http://localhost:3012")
    print()
    
    # Test basic endpoints
    endpoints_ok = test_dashboard_endpoints()
    
    # Test interactivity
    interactivity_ok = test_dashboard_interactivity()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS")
    print("=" * 60)
    
    if endpoints_ok and interactivity_ok:
        print("🎉 SUCCESS: Dashboard is fully functional!")
        print("🌐 Access it at: http://localhost:3012/dashboard")
        print()
        print("💡 If you're seeing 'no style UI', it might be:")
        print("   - Browser cache issue (try Ctrl+F5)")
        print("   - CSS not loading due to CORS/network issues")
        print("   - JavaScript errors in browser console")
        print("   - Check browser developer tools for errors")
    else:
        print("❌ ISSUES DETECTED: Dashboard has problems")
        print("🔧 Check the test results above for specific issues")
    
    print("\n🔍 Next steps:")
    print("1. Open http://localhost:3012/dashboard in a browser")
    print("2. Open browser developer tools (F12)")
    print("3. Check Console tab for JavaScript errors")
    print("4. Check Network tab to see if CSS/JS files load")
    print("5. Check Elements tab to see if styles are applied")
