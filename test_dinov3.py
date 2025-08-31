#!/usr/bin/env python3
"""
Quick DINOv3 functionality test
"""
import torch
from transformers import AutoModel, AutoImageProcessor
from PIL import Image
import sys

def test_dinov3():
    """Test DINOv3 model functionality"""
    try:
        print('=== Quick DINOv3 Test ===')
        print(f'PyTorch: {torch.__version__}')
        print(f'CUDA: {torch.cuda.is_available()}')
        
        if torch.cuda.is_available():
            print(f'GPU: {torch.cuda.get_device_name(0)}')
        
        print('\nLoading DINOv3 model...')
        
        # Load model
        model = AutoModel.from_pretrained(
            'models/dinov3-vitb16-pretrain-lvd1689m', 
            trust_remote_code=True, 
            local_files_only=True
        )
        print('✓ Model loaded')
        
        # Load processor
        processor = AutoImageProcessor.from_pretrained(
            'models/dinov3-vitb16-pretrain-lvd1689m', 
            local_files_only=True
        )
        print('✓ Processor loaded')
        
        # Move to GPU
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = model.to(device)
        print(f'✓ Model moved to {device}')
        
        # Test with dummy image
        print('\nTesting inference...')
        dummy_image = Image.new('RGB', (224, 224), color='blue')
        inputs = processor(dummy_image, return_tensors='pt')
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        print(f'✓ Inference successful!')
        print(f'Output shape: {outputs.last_hidden_state.shape}')
        print(f'Feature dimension: {outputs.last_hidden_state.shape[-1]}')
        print('\n🎉 DINOv3 is working perfectly!')
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        print(f'Error type: {type(e).__name__}')
        return False

if __name__ == "__main__":
    success = test_dinov3()
    sys.exit(0 if success else 1)
