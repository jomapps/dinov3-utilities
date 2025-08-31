#!/usr/bin/env python3
"""
Install basic dependencies for DINOv3 utilities
"""
import subprocess
import sys
import os

def install_package(package_name):
    """Install a single package"""
    print(f"Installing {package_name}...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name, "--no-cache-dir"
        ], check=True, capture_output=True, text=True, timeout=60)
        
        print(f"✓ {package_name} installed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"⚠️  {package_name} installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def test_imports():
    """Test if packages can be imported"""
    print("\nTesting imports...")
    
    packages = {
        'dotenv': 'python-dotenv',
        'requests': 'requests', 
        'huggingface_hub': 'huggingface_hub',
        'transformers': 'transformers'
    }
    
    results = {}
    
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} imports successfully")
            results[package_name] = True
        except ImportError:
            print(f"❌ {package_name} import failed")
            results[package_name] = False
    
    return results

def main():
    print("=== Installing DINOv3 Dependencies ===")
    
    # List of packages to install
    packages = [
        "python-dotenv",
        "requests", 
        "huggingface_hub",
        "transformers"
    ]
    
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
        print()  # Empty line for readability
    
    print(f"Installation complete: {success_count}/{len(packages)} packages installed")
    
    # Test imports
    import_results = test_imports()
    
    working_packages = sum(import_results.values())
    print(f"\nImport test: {working_packages}/{len(import_results)} packages working")
    
    if working_packages == len(import_results):
        print("\n🎉 All dependencies installed and working!")
        return True
    else:
        print("\n⚠️  Some dependencies failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
