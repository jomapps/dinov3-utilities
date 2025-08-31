#!/usr/bin/env python3
"""
Test DINOv3 model access step by step
"""
from dotenv import load_dotenv
import os
import torch

# Load environment variables
load_dotenv()

def test_dinov3_model():
    """Test DINOv3 model loading step by step"""
    
    print("=== DINOv3 Model Access Test ===")
    
    # Step 1: Check token
    hf_token = os.getenv('HF_TOKEN')
    print(f"✓ HF Token: {hf_token[:10]}...")
    
    # Step 2: Login to HF
    from huggingface_hub import login
    login(token=hf_token)
    print("✓ Logged into Hugging Face")
    
    # Step 3: Test PyTorch
    print(f"✓ PyTorch: {torch.__version__}")
    print(f"✓ CUDA: {torch.cuda.is_available()}")
    
    # Step 4: Try to access the model
    model_name = "facebook/dinov3-vitb16-pretrain-lvd1689m"
    print(f"\nTesting access to: {model_name}")
    
    try:
        from transformers import AutoModel, AutoImageProcessor
        
        print("Loading model...")
        model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            token=hf_token
        )
        print("✓ Model loaded successfully!")
        
        print("Loading processor...")
        processor = AutoImageProcessor.from_pretrained(
            model_name,
            token=hf_token
        )
        print("✓ Processor loaded successfully!")
        
        # Test GPU if available
        if torch.cuda.is_available():
            print("Moving to GPU...")
            model = model.to('cuda')
            print("✓ Model on GPU")
        
        print(f"\n🎉 DINOv3 model ready!")
        print(f"Model type: {type(model)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    success = test_dinov3_model()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
