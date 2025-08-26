#!/usr/bin/env python3
"""
iOS İçin Kıyafet Arka Plan Kaldırıcı API Test Script
Bu script iOS projenden nasıl kullanılacağını gösterir
"""

import requests
import json
import base64
import os

def test_ios_api():
    """
    iOS için API test fonksiyonu
    """
    
    # API endpoint
    api_url = "http://localhost:5001/api/remove-background-base64"
    
    # Test görüntüsünü base64'e çevir
    with open("test2.png", "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # iOS'dan gönderilecek payload
    payload = {
        "image_base64": base64_string,
        "model": "ultra",        # "ultra" veya "advanced"
        "positioning": "smart",  # "smart" veya "center"
        "enhance": False,        # Şeffaf PNG için false
        "create_variants": False  # Base64 için varyant kapalı
    }
    
    print("📱 iOS API Test Başlıyor...")
    print(f"🌐 Endpoint: {api_url}")
    print(f"📦 Payload boyutu: {len(json.dumps(payload))} bytes")
    print(f"🖼️  Base64 boyutu: {len(base64_string)} karakter")
    
    try:
        # API isteği gönder
        response = requests.post(
            api_url,
            json=payload,
            headers={
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Test Başarılı!")
            print(f"⏱️  İşlem süresi: {result['processing_time']:.2f} saniye")
            print(f"🤖 Kullanılan model: {result['model_used']}")
            print(f"� Base64 boyutu: {len(result['result_base64'])} karakter")
            print(f"✨ Şeffaf PNG oluşturuldu!")
            
            # Base64'ü dosyaya kaydet (test için)
            decoded_data = base64.b64decode(result['result_base64'])
            with open("test_sonuc_seffaf.png", "wb") as f:
                f.write(decoded_data)
            print(f"💾 Sonuç kaydedildi: test_sonuc_seffaf.png")
            
            return True
            
        else:
            print(f"❌ API Hatası: {response.status_code}")
            print(f"Hata: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

def generate_ios_swift_example():
    """
    iOS Swift kullanım örneği oluştur
    """
    
    swift_code = '''
// iOS Swift Kullanım Örneği
// Kıyafet Arka Plan Kaldırıcı API

import Foundation
import UIKit

class ClothingBackgroundRemover {
    
    let apiBaseURL = "http://localhost:5001"  // Gerçek IP adresinizi kullanın
    
    func removeBackground(from image: UIImage, 
                         model: String = "ultra",
                         positioning: String = "smart",
                         completion: @escaping (Result<BackgroundRemovalResult, Error>) -> Void) {
        
        // 1. Görüntüyü base64'e çevir
        guard let imageData = image.pngData(),
              let base64String = imageData.base64EncodedString() else {
            completion(.failure(NSError(domain: "ImageConversion", code: 1)))
            return
        }
        
        // 2. API payload hazırla
        let payload: [String: Any] = [
            "image_base64": base64String,
            "model": model,
            "positioning": positioning,
            "enhance": true,
            "create_variants": true
        ]
        
        // 3. API isteği gönder
        guard let url = URL(string: "\\(apiBaseURL)/api/remove-background-base64") else {
            completion(.failure(NSError(domain: "InvalidURL", code: 2)))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        } catch {
            completion(.failure(error))
            return
        }
        
        // 4. İstek gönder
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "NoData", code: 3)))
                return
            }
            
            do {
                let result = try JSONDecoder().decode(BackgroundRemovalResponse.self, from: data)
                if result.success {
                    completion(.success(result.result))
                } else {
                    completion(.failure(NSError(domain: "APIError", code: 4, userInfo: ["message": result.error ?? "Unknown error"])))
                }
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    // İşlenmiş görüntüyü indir
    func downloadProcessedImage(from urlString: String, completion: @escaping (UIImage?) -> Void) {
        guard let url = URL(string: "\\(apiBaseURL)\\(urlString)") else {
            completion(nil)
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            guard let data = data, let image = UIImage(data: data) else {
                completion(nil)
                return
            }
            
            DispatchQueue.main.async {
                completion(image)
            }
        }.resume()
    }
}

// MARK: - Data Models

struct BackgroundRemovalResponse: Codable {
    let success: Bool
    let result: BackgroundRemovalResult
    let variants: [ImageVariant]?
    let error: String?
}

struct BackgroundRemovalResult: Codable {
    let filename: String
    let downloadUrl: String
    let modelUsed: String
    let processingTime: Double
    let sizeBytes: Int
    
    enum CodingKeys: String, CodingKey {
        case filename
        case downloadUrl = "download_url"
        case modelUsed = "model_used"
        case processingTime = "processing_time"
        case sizeBytes = "size_bytes"
    }
}

struct ImageVariant: Codable {
    let filename: String
    let downloadUrl: String
    let sizeBytes: Int
    
    enum CodingKeys: String, CodingKey {
        case filename
        case downloadUrl = "download_url"
        case sizeBytes = "size_bytes"
    }
}

// MARK: - Kullanım Örneği

class ViewController: UIViewController {
    
    let backgroundRemover = ClothingBackgroundRemover()
    
    @IBAction func removeBackgroundTapped(_ sender: UIButton) {
        guard let image = imageView.image else { return }
        
        backgroundRemover.removeBackground(from: image, model: "ultra") { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let bgResult):
                    print("✅ Başarılı! Model: \\(bgResult.modelUsed)")
                    print("⏱️ Süre: \\(bgResult.processingTime)s")
                    
                    // Ana dosyayı indir
                    self.backgroundRemover.downloadProcessedImage(from: bgResult.downloadUrl) { processedImage in
                        self.imageView.image = processedImage
                    }
                    
                case .failure(let error):
                    print("❌ Hata: \\(error.localizedDescription)")
                }
            }
        }
    }
}
'''
    
    with open("iOS_Swift_Example.swift", "w", encoding="utf-8") as f:
        f.write(swift_code)
    
    print("📱 iOS Swift örneği oluşturuldu: iOS_Swift_Example.swift")

if __name__ == "__main__":
    print("🧪 API Test ve iOS Örneği Oluşturucu")
    print("="*50)
    
    # 1. API test et
    if test_ios_api():
        print("\n🎉 API test başarılı!")
    else:
        print("\n❌ API test başarısız!")
    
    # 2. iOS Swift örneği oluştur
    print("\n📱 iOS Swift örneği oluşturuluyor...")
    generate_ios_swift_example()
    
    print("\n✅ Tüm işlemler tamamlandı!")
    print("📱 iOS projenizden http://localhost:5001 adresine istek atabilirsiniz!")
