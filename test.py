import base64
import requests

# test.png'yi base64'e çevir
with open('test.png', 'rb') as f:
    image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')

payload = {
    'image_base64': image_base64,
    'model': 'ultra',
    'positioning': 'smart'
}

print('🔥 RAILWAY CLOTHING AI TEST!')
print('🚀 API: https://rembg-api-production-6b7e.up.railway.app')

try:
    response = requests.post(
        'https://rembg-api-production-6b7e.up.railway.app/api/remove-background-base64',
        json=payload,
        timeout=300
    )
    
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print(f'✅ SUCCESS: {result.get("success")}')
        print(f'🤖 Model: {result.get("model_used")}')
        print(f'⏱️ Time: {result.get("processing_time")}s')
        
        if result.get('success') and 'result_base64' in result:
            result_data = base64.b64decode(result['result_base64'])
            with open('railway_result.png', 'wb') as f:
                f.write(result_data)
            print(f'🎉 BAŞARILI! railway_result.png saved')
            print(f'📊 {len(image_data)} -> {len(result_data)} bytes')
    else:
        print(f'❌ Error: {response.status_code}')
        print(response.text)
        
except Exception as e:
    print(f'❌ Request failed: {e}')