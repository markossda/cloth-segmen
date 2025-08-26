
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
        guard let url = URL(string: "\(apiBaseURL)/api/remove-background-base64") else {
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
        guard let url = URL(string: "\(apiBaseURL)\(urlString)") else {
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
                    print("✅ Başarılı! Model: \(bgResult.modelUsed)")
                    print("⏱️ Süre: \(bgResult.processingTime)s")
                    
                    // Ana dosyayı indir
                    self.backgroundRemover.downloadProcessedImage(from: bgResult.downloadUrl) { processedImage in
                        self.imageView.image = processedImage
                    }
                    
                case .failure(let error):
                    print("❌ Hata: \(error.localizedDescription)")
                }
            }
        }
    }
}
