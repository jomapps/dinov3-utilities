#!/usr/bin/env python3
"""
Test local DINOv3 model loading
"""
import os
import torch
from transformers import AutoModel, AutoImageProcessor
from PIL import Image
import numpy as np

def test_local_model():
    """Test loading DINOv3 model from local files"""
    
    print("=== Local DINOv3 Model Test ===")
    
    # Model path
    model_path = "models/dinov3-vitb16-pretrain-lvd1689m"
    
    # Check if files exist
    required_files = ["config.json", "model.safetensors", "preprocessor_config.json"]
    
    print("Checking model files...")
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✓ {file}: {size:,} bytes")
        else:
            print(f"❌ {file}: NOT FOUND")
            return False
    
    # Test PyTorch
    print(f"\n✓ PyTorch: {torch.__version__}")
    print(f"✓ CUDA: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
    
    try:
        # Load model from local files
        print(f"\nLoading model from: {model_path}")
        model = AutoModel.from_pretrained(
            model_path,
            trust_remote_code=True,
            local_files_only=True
        )
        print("✓ Model loaded successfully!")
        
        # Load processor
        print("Loading image processor...")
        processor = AutoImageProcessor.from_pretrained(
            model_path,
            local_files_only=True
        )
        print("✓ Processor loaded successfully!")
        
        # Move to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        print(f"✓ Model moved to: {device}")
        
        # Test with a dummy image
        print("\nTesting with dummy image...")
        dummy_image = Image.new('RGB', (224, 224), color='red')
        
        # Process image
        inputs = processor(dummy_image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Run inference
        with torch.no_grad():
            outputs = model(**inputs)
        
        print(f"✓ Inference successful!")
        print(f"Output shape: {outputs.last_hidden_state.shape}")
        print(f"Feature dimension: {outputs.last_hidden_state.shape[-1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    success = test_local_model()
    if success:
        print("\n🎉 DINOv3 local model is working perfectly!")
        print("Ready for production use!")
    else:
        print("\n❌ Local model test failed")
