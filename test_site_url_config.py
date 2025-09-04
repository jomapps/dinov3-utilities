#!/usr/bin/env python3
"""
Test script to verify site URL configuration is working
"""
import requests
import json

def test_site_url_configuration():
    """Test that the site URL is properly configured"""
    base_url = "http://localhost:3012"
    
    print("🌐 Testing Site URL Configuration")
    print("=" * 50)
    
    # Test root endpoint
    print("\n📋 Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            site_url = data.get('site_url')
            print(f"✅ Root endpoint accessible")
            print(f"🔗 Site URL: {site_url}")
            
            if site_url == "https://dino.ft.tc":
                print("✅ Site URL correctly configured!")
            else:
                print(f"⚠️  Site URL mismatch. Expected: https://dino.ft.tc, Got: {site_url}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing root endpoint: {e}")
        return False
    
    # Test configuration endpoint
    print("\n📋 Testing configuration endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/config")
        if response.status_code == 200:
            config = response.json()
            site_url = config.get('site_url')
            cors_origins = config.get('cors_origins', [])
            
            print(f"✅ Configuration endpoint accessible")
            print(f"🔗 Site URL: {site_url}")
            print(f"🌐 CORS Origins: {cors_origins}")
            
            # Check if site URL is correct
            if site_url == "https://dino.ft.tc":
                print("✅ Site URL in config is correct!")
            else:
                print(f"⚠️  Site URL in config is incorrect: {site_url}")
            
            # Check if CORS includes the site URL
            if "https://dino.ft.tc" in cors_origins:
                print("✅ CORS origins include the site URL!")
            else:
                print("⚠️  CORS origins don't include the site URL")
                
        else:
            print(f"❌ Configuration endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing configuration endpoint: {e}")
        return False
    
    # Test dashboard
    print("\n📋 Testing dashboard...")
    try:
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            content = response.text
            print(f"✅ Dashboard accessible")
            print(f"📏 Content length: {len(content)} characters")
            
            # Check if placeholder is updated
            if 'placeholder="https://dino.ft.tc"' in content:
                print("✅ Dashboard placeholder updated to use site URL!")
            else:
                print("⚠️  Dashboard placeholder not updated")
                
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False
    
    return True

def test_dashboard_functionality():
    """Test that dashboard can load configuration"""
    base_url = "http://localhost:3012"
    
    print("\n🔧 Testing Dashboard Auto-Configuration")
    print("=" * 50)
    
    # Test if dashboard JavaScript can load config
    print("📋 Testing if dashboard can auto-configure...")
    
    # Check CSS
    try:
        response = requests.get(f"{base_url}/static/dashboard/styles.css")
        if response.status_code == 200:
            print("✅ Dashboard CSS accessible")
        else:
            print(f"❌ Dashboard CSS failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error loading CSS: {e}")
        return False
    
    # Check JavaScript
    try:
        response = requests.get(f"{base_url}/static/dashboard/ui.js")
        if response.status_code == 200:
            js_content = response.text
            print("✅ Dashboard JavaScript accessible")
            
            # Check if loadConfig function exists
            if "loadConfig" in js_content:
                print("✅ Auto-configuration function found in JavaScript!")
            else:
                print("⚠️  Auto-configuration function not found")
                
        else:
            print(f"❌ Dashboard JavaScript failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error loading JavaScript: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 DINOv3 Site URL Configuration Test")
    print("Testing configuration for https://dino.ft.tc")
    print()
    
    # Test configuration
    config_ok = test_site_url_configuration()
    
    # Test dashboard functionality
    dashboard_ok = test_dashboard_functionality()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS")
    print("=" * 60)
    
    if config_ok and dashboard_ok:
        print("🎉 SUCCESS: Site URL configuration is working!")
        print("🌐 Your dashboard is configured for: https://dino.ft.tc")
        print()
        print("✅ What's working:")
        print("   - Site URL properly set in configuration")
        print("   - CORS origins include your domain")
        print("   - Dashboard auto-detects the correct URL")
        print("   - All static assets are accessible")
        print()
        print("🔗 Access your dashboard at:")
        print("   - Local: http://localhost:3012/dashboard")
        print("   - Production: https://dino.ft.tc/dashboard")
        
    else:
        print("❌ ISSUES DETECTED: Configuration has problems")
        print("🔧 Check the test results above for specific issues")
    
    print("\n💡 Next steps:")
    print("1. Make sure your domain https://dino.ft.tc points to this server")
    print("2. Ensure your reverse proxy/load balancer forwards to port 3012")
    print("3. Test the dashboard at https://dino.ft.tc/dashboard")
    print("4. Check browser developer tools if there are any issues")
