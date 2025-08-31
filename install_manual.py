#!/usr/bin/env python3
"""
Manual installation script for DINOv3 dependencies
"""
import os
import subprocess
import sys

def install_wheels():
    """Install wheel files manually"""
    wheels_dir = "wheels"
    
    if not os.path.exists(wheels_dir):
        print(f"❌ {wheels_dir} directory not found!")
        print("Please create the directory and download the wheel files first.")
        return False
    
    # List of wheel files to install in order (dependencies first)
    wheel_files = [
        "requests-2.31.0-py3-none-any.whl",
        "python_dotenv-1.0.0-py3-none-any.whl", 
        "huggingface_hub-0.20.3-py3-none-any.whl",
        "transformers-4.36.2-py3-none-any.whl"
    ]
    
    print("Installing wheel files...")
    
    for wheel_file in wheel_files:
        wheel_path = os.path.join(wheels_dir, wheel_file)
        
        if not os.path.exists(wheel_path):
            print(f"⚠️  {wheel_file} not found, skipping...")
            continue
            
        print(f"Installing {wheel_file}...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                wheel_path, "--no-deps", "--force-reinstall"
            ], check=True, capture_output=True, text=True)
            
            print(f"✓ {wheel_file} installed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {wheel_file}: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    return True

def test_installation():
    """Test if the installation worked"""
    print("\nTesting installation...")
    
    try:
        # Test dotenv
        from dotenv import load_dotenv
        print("✓ python-dotenv working")
        
        # Test huggingface_hub
        from huggingface_hub import login
        print("✓ huggingface_hub working")
        
        # Test transformers
        from transformers import AutoModel
        print("✓ transformers working")
        
        # Test PyTorch
        import torch
        print(f"✓ PyTorch {torch.__version__} working")
        print(f"✓ CUDA: {torch.cuda.is_available()}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    print("=== Manual DINOv3 Dependencies Installation ===")
    
    if install_wheels():
        print("\n✅ Wheel installation completed!")
        
        if test_installation():
            print("\n🎉 All dependencies are working!")
        else:
            print("\n❌ Some dependencies failed to import")
    else:
        print("\n❌ Wheel installation failed")
