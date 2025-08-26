#!/usr/bin/env python3
"""
API Test Script - Background removal test
"""
import requests
import base64
import json
from PIL import Image
import io

# Test için basit bir resim oluştur
def create_test_image():
    # 100x100 kırmızı kare oluştur
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()

def test_base64_api(api_url):
    """Base64 API test"""
    print(f"🧪 Testing Base64 API: {api_url}")
    
    # Test image oluştur
    image_data = create_test_image()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # API request
    payload = {
        'image_base64': image_base64,
        'model': 'ultra',
        'positioning': 'smart'
    }
    
    try:
        response = requests.post(
            f"{api_url}/api/remove-background-base64",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ API çalışıyor!")
                return True
            else:
                print(f"❌ API error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    return False

def test_health_api(api_url):
    """Health check test"""
    print(f"🏥 Testing Health API: {api_url}")
    
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    # Test URL'leri
    local_url = "http://localhost:8080"
    deployed_url = "https://YOUR_DEPLOYED_URL"  # Deployed URL'ini buraya koy
    
    print("=" * 50)
    print("🚀 API TEST BAŞLIYOR")
    print("=" * 50)
    
    # Önce health check
    if test_health_api(local_url):
        # Sonra API test
        test_base64_api(local_url)
    else:
        print("❌ Server çalışmıyor veya erişilemiyor")