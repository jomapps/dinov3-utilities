#!/usr/bin/env python3
"""
Minimal DINOv3 test without external dependencies
"""
import os
import torch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_basic_access():
    """Test basic model access"""
    print("=== DINOv3 Access Test ===")
    
    # Test PyTorch
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Try to download model weights directly
    try:
        print("\nTesting direct model download...")
        
        # Use torch.hub to download DINOv3 weights
        import torch.hub
        
        # Try the official DINOv3 weights
        model_url = "https://dl.fbaipublicfiles.com/dinov3/dinov3_vitb16_pretrain.pth"
        print(f"Downloading from: {model_url}")
        
        state_dict = torch.hub.load_state_dict_from_url(
            model_url, 
            progress=True,
            map_location='cpu'
        )
        
        print(f"✓ Model loaded! Keys: {len(state_dict.keys())}")
        
        # Check some key names
        keys = list(state_dict.keys())[:5]
        print(f"Sample keys: {keys}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_access()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
