#!/usr/bin/env python3
import requests
import base64
import time

print('🔥 Quick Railway API Test')

# Çok küçük 1x1 pixel test image
test_image = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc```\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')

payload = {
    'image_base64': test_image,
    'model': 'advanced',  # Advanced daha hızlı
    'positioning': 'center'
}

print('📡 Testing with minimal image...')

try:
    start_time = time.time()
    response = requests.post(
        'https://rembg-api-production-6b7e.up.railway.app/api/remove-background-base64',
        json=payload,
        timeout=180  # 3 dakika timeout
    )
    
    elapsed = time.time() - start_time
    print(f'⏱️ Response time: {elapsed:.2f}s')
    print(f'📊 Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print(f'✅ Success: {result.get("success")}')
        print(f'🤖 Model: {result.get("model_used")}')
        print(f'⏱️ Processing: {result.get("processing_time")}s')
    else:
        print(f'❌ Error: {response.text}')
        
except Exception as e:
    print(f'❌ Exception: {e}')