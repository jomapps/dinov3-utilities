#!/usr/bin/env python3
"""
Test DINOv3 model access with Hugging Face token
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_dinov3_access():
    """Test DINOv3 model access with proper HF token authentication"""
    
    # Get HF token from environment
    hf_token = os.getenv('HF_TOKEN')
    if not hf_token:
        print("❌ HF_TOKEN not found in environment")
        return False
    
    print(f"✓ Found HF token: {hf_token[:10]}...")
    
    try:
        # Test PyTorch and CUDA
        import torch
        print(f"✓ PyTorch {torch.__version__} loaded")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
        
        # Test transformers library
        try:
            from transformers import AutoModel, AutoImageProcessor
            print("✓ Transformers library available")
        except ImportError:
            print("❌ Transformers library not installed")
            print("Installing transformers...")
            os.system("pip install transformers")
            from transformers import AutoModel, AutoImageProcessor
            print("✓ Transformers installed and imported")
        
        # Test huggingface_hub
        try:
            from huggingface_hub import login
            print("✓ Hugging Face Hub available")
        except ImportError:
            print("❌ Hugging Face Hub not installed")
            print("Installing huggingface_hub...")
            os.system("pip install huggingface_hub")
            from huggingface_hub import login
            print("✓ Hugging Face Hub installed and imported")
        
        # Login with token
        print("Logging in to Hugging Face...")
        login(token=hf_token)
        print("✓ Successfully logged in to Hugging Face")
        
        # Test model access
        model_name = "facebook/dinov3-vitb16-pretrain-lvd1689m"
        print(f"Testing access to {model_name}...")
        
        # Try to load the model
        print("Loading DINOv3 model...")
        model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            token=hf_token
        )
        print("✓ DINOv3 model loaded successfully!")
        
        # Try to load the processor
        print("Loading image processor...")
        processor = AutoImageProcessor.from_pretrained(
            model_name,
            token=hf_token
        )
        print("✓ Image processor loaded successfully!")
        
        # Test GPU loading if available
        if torch.cuda.is_available():
            print("Moving model to GPU...")
            model = model.to('cuda')
            print("✓ Model moved to GPU successfully!")
        
        print("\n🎉 All tests passed! DINOv3 is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_dinov3_access()
    if success:
        print("\n✅ DINOv3 setup complete and working!")
    else:
        print("\n❌ DINOv3 setup failed. Check the errors above.")
