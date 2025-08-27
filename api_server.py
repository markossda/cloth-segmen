#!/usr/bin/env python3
"""
Kıyafet Arka Plan Kaldırıcı - Web API Server
iOS projesi için REST API endpoint'leri
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from pathlib import Path
import time
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64

# Kendi modüllerimizi import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# AI modelleri sadece gerektiğinde import et
UltraClothingBgRemover = None
AdvancedClothingBgRemover = None

app = Flask(__name__)
CORS(app)  # iOS'tan istek gelebilsin

# Konfigürasyon
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Klasörleri oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Global remover'lar (bir kez yüklensin)
ultra_remover = None
advanced_remover = None

def init_removers():
    """
    Remover'ları başlat - AI modelleri zorla yükle
    """
    global ultra_remover, advanced_remover, UltraClothingBgRemover, AdvancedClothingBgRemover
    
    print("🚀 AI modelleri zorla yükleniyor...")
    print("💾 Memory usage check - başlangıç")
    
    try:
        # Lightweight clothing remover import et
        print("🔄 Clothing AI modüllerini import ediliyor...")
        print("📦 ClothingRemover import ediliyor...")
        from clothing_remover import UltraClothingBgRemover, AdvancedClothingBgRemover
        print("✅ Clothing modülleri import edildi")
        
        print("✅ Tüm AI modülleri import edildi")
        
        print("🤖 Ultra AI modeli yükleniyor...")
        print("⏳ Bu işlem 2-5 dakika sürebilir...")
        start_time = time.time()
        ultra_remover = UltraClothingBgRemover()
        ultra_time = time.time() - start_time
        print(f"✅ Ultra model yüklendi! ({ultra_time:.2f}s)")
        
        print("🤖 Advanced AI modeli yükleniyor...")
        start_time = time.time()
        advanced_remover = AdvancedClothingBgRemover('u2net_cloth_seg')
        advanced_time = time.time() - start_time
        print(f"✅ Advanced model yüklendi! ({advanced_time:.2f}s)")
        
        total_time = ultra_time + advanced_time
        print(f"🎉 Tüm AI modelleri hazır! Toplam süre: {total_time:.2f}s")
        print("💾 Memory usage check - bitiş")
        
    except ImportError as e:
        print(f"❌ AI modül import hatası: {e}")
        print("🔍 Import stack trace:")
        import traceback
        traceback.print_exc()
        raise e
    except Exception as e:
        print(f"❌ Model yükleme hatası: {e}")
        print("🔍 Loading stack trace:")
        import traceback
        traceback.print_exc()
        raise e

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """
    Benzersiz dosya adı oluştur
    """
    timestamp = str(int(time.time()))
    unique_id = str(uuid.uuid4())[:8]
    extension = original_filename.rsplit('.', 1)[1].lower()
    return f"{timestamp}_{unique_id}.{extension}"

@app.route('/', methods=['GET'])
def index():
    """
    Ana sayfa - API dokümantasyonu
    """
    return jsonify({
        'service': 'Kıyafet Arka Plan Kaldırıcı API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': 'GET /health',
            'remove_background': 'POST /api/remove-background',
            'remove_background_base64': 'POST /api/remove-background-base64',
            'download': 'GET /api/download/<filename>',
            'preview': 'GET /api/preview/<filename>'
        },
        'example_usage': {
            'swift_code': '''
let url = URL(string: "YOUR_API_URL/api/remove-background-base64")!
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")

let parameters: [String: Any] = [
    "image_base64": imageBase64String,
    "model": "ultra",
    "positioning": "smart"
]

request.httpBody = try? JSONSerialization.data(withJSONObject: parameters)

URLSession.shared.dataTask(with: request) { data, response, error in
    if let data = data {
        let result = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
        let resultBase64 = result?["result_base64"] as? String
        // resultBase64'ü kullanarak görüntüyü gösterin
    }
}.resume()
            '''
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """
    Server sağlık kontrolü
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'models_loaded': ultra_remover is not None and advanced_remover is not None,
        'version': '1.0.0'
    }), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    """
    API durumu
    """
    status = {
        'server': 'running',
        'timestamp': time.time(),
        'ultra_model_loaded': ultra_remover is not None,
        'advanced_model_loaded': advanced_remover is not None,
        'version': '1.0.0',
        'endpoints': [
            'POST /api/remove-background',
            'POST /api/remove-background-base64',
            'GET /api/status',
            'GET /api/models'
        ]
    }
    
    if ultra_remover:
        status['ultra_model'] = getattr(ultra_remover, 'best_model', 'ultra')
    if advanced_remover:
        status['advanced_model'] = getattr(advanced_remover, 'model_name', 'advanced')
    
    return jsonify(status)

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """
    Mevcut AI modellerini listele
    """
    models = {
        'ultra': {
            'name': 'ULTRA AI Model',
            'description': 'En gelişmiş AI modelleri ile otomatik optimizasyon',
            'features': ['Akıllı konumlandırma', 'AI destekli ön işleme', 'Ultra kalite'],
            'recommended': True
        },
        'advanced': {
            'name': 'Gelişmiş Model', 
            'description': 'Boyut düzeltmeli ve manuel model seçimi',
            'features': ['Boyut optimizasyonu', 'Konumlandırma düzeltmesi'],
            'recommended': False
        }
    }
    
    return jsonify({
        'success': True,
        'models': models,
        'default': 'ultra'
    })


@app.route('/api/remove-background', methods=['POST'])
def remove_background():
    """
    Ana arka plan kaldırma endpoint'i
    """
    global ultra_remover, advanced_remover
    
    try:
        # Request validation
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Görüntü dosyası bulunamadı'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Dosya seçilmedi'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Desteklenmeyen dosya formatı'
            }), 400
        
        # Parametreler
        model_type = request.form.get('model', 'ultra')
        positioning = request.form.get('positioning', 'smart')
        create_variants = request.form.get('variants', 'false').lower() == 'true'
        enhance = request.form.get('enhance', 'false').lower() == 'true'
        
        # Dosyayı kaydet
        filename = generate_unique_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        print(f"📁 Dosya kaydedildi: {filename}")
        print(f"⚙️  Parametreler: model={model_type}, positioning={positioning}")
        
        start_time = time.time()
        
        # Model seçimi ve işlem - Lazy loading destekli
        if model_type == 'ultra':
            if not ultra_remover:
                print("🔄 Lazy loading: Ultra model yükleniyor...")
                try:
                    from clothing_remover import UltraClothingBgRemover
                    ultra_remover = UltraClothingBgRemover()
                    print("✅ Ultra model lazy loading tamamlandı")
                except Exception as e:
                    print(f"❌ Ultra model lazy loading hatası: {e}")
                    return jsonify({
                        'success': False,
                        'error': f'Ultra model yüklenemedi: {str(e)}'
                    }), 500
            options = {
                'ai_positioning': True,
                'enhance': enhance,
                'create_variants': create_variants,
                'positioning_mode': positioning
            }
            result_path = ultra_remover.ultra_process(filepath, options)
            used_model = ultra_remover.best_model
        elif model_type == 'advanced':
            if not advanced_remover:
                print("🔄 Lazy loading: Advanced model yükleniyor...")
                try:
                    from clothing_remover import AdvancedClothingBgRemover
                    advanced_remover = AdvancedClothingBgRemover('u2net_cloth_seg')
                    print("✅ Advanced model lazy loading tamamlandı")
                except Exception as e:
                    print(f"❌ Advanced model lazy loading hatası: {e}")
                    return jsonify({
                        'success': False,
                        'error': f'Advanced model yüklenemedi: {str(e)}'
                    }), 500
            options = {
                'preprocess': True,
                'fix_positioning': True,
                'center_vertically': positioning == 'center',
                'enhance': enhance,
                'create_variants': create_variants,
                'add_padding': True
            }
            result_path = advanced_remover.process_clothing_complete(filepath, options)
            used_model = advanced_remover.model_name
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz model türü'
            }), 400
        
        process_time = time.time() - start_time
        
        if not result_path or not os.path.exists(result_path):
            return jsonify({
                'success': False,
                'error': 'İşlem başarısız oldu'
            }), 500
        
        # Sonuç dosyasını processed klasörüne taşı
        result_filename = os.path.basename(result_path)
        final_path = os.path.join(PROCESSED_FOLDER, result_filename)
        
        if os.path.exists(result_path):
            os.rename(result_path, final_path)
        
        # Orijinal dosyayı sil
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Başarılı response
        file_size = os.path.getsize(final_path)
        
        response_data = {
            'success': True,
            'result': {
                'filename': result_filename,
                'size_bytes': file_size,
                'processing_time': round(process_time, 2),
                'model_used': used_model,
                'download_url': f'/api/download/{result_filename}'
            },
            'parameters': {
                'model_type': model_type,
                'positioning': positioning,
                'enhance': enhance,
                'create_variants': create_variants
            }
        }
        
        print(f"✅ İşlem başarılı: {process_time:.2f}s, Model: {used_model}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ API hatası: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/remove-background-base64', methods=['POST'])
def remove_background_base64():
    """
    Base64 formatında görüntü işleme (iOS için alternatif)
    """
    global ultra_remover, advanced_remover
    
    try:
        data = request.get_json()
        
        if 'image_base64' not in data:
            return jsonify({
                'success': False,
                'error': 'image_base64 parametresi gerekli'
            }), 400
        
        # Base64'ü decode et
        image_data = base64.b64decode(data['image_base64'])
        
        # Geçici dosya oluştur
        filename = f"temp_{int(time.time())}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # Parametreler
        model_type = data.get('model', 'ultra')
        positioning = data.get('positioning', 'smart')
        enhance = data.get('enhance', False)
        create_variants = data.get('create_variants', False)
        
        print(f"📱 Base64 işlem: model={model_type}, positioning={positioning}")
        
        start_time = time.time()
        
        # İşlem - Sadece gerçek AI modelleri
        if model_type == 'ultra':
            if not ultra_remover:
                return jsonify({
                    'success': False,
                    'error': 'Ultra model yüklenmedi'
                }), 500
            options = {
                'ai_positioning': True,
                'enhance': enhance,
                'create_variants': create_variants,
                'positioning_mode': positioning
            }
            result_path = ultra_remover.ultra_process(filepath, options)
            used_model = ultra_remover.best_model
        elif model_type == 'advanced':
            if not advanced_remover:
                print("🔄 Lazy loading: Advanced model yükleniyor...")
                try:
                    from clothing_remover import AdvancedClothingBgRemover
                    advanced_remover = AdvancedClothingBgRemover('u2net_cloth_seg')
                    print("✅ Advanced model lazy loading tamamlandı")
                except Exception as e:
                    print(f"❌ Advanced model lazy loading hatası: {e}")
                    return jsonify({
                        'success': False,
                        'error': f'Advanced model yüklenemedi: {str(e)}'
                    }), 500
            options = {
                'preprocess': True,
                'fix_positioning': True,
                'center_vertically': positioning == 'center',
                'enhance': enhance,
                'create_variants': create_variants,
                'add_padding': True
            }
            result_path = advanced_remover.process_clothing_complete(filepath, options)
            used_model = advanced_remover.model_name
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz model türü'
            }), 400
        
        process_time = time.time() - start_time
        
        if not result_path or not os.path.exists(result_path):
            return jsonify({
                'success': False,
                'error': 'İşlem başarısız'
            }), 500
        
        # Sonucu base64'e çevir
        with open(result_path, 'rb') as f:
            result_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Geçici dosyaları temizle
        for temp_file in [filepath, result_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        response_data = {
            'success': True,
            'result_base64': result_base64,
            'processing_time': round(process_time, 2),
            'model_used': used_model,
            'parameters': {
                'model_type': model_type,
                'positioning': positioning
            }
        }
        
        print(f"📱 Base64 işlem başarılı: {process_time:.2f}s")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Base64 API hatası: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    İşlenmiş dosyaları indir
    """
    try:
        file_path = os.path.join(PROCESSED_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({
                'success': False,
                'error': 'Dosya bulunamadı'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/preview/<filename>', methods=['GET'])
def preview_file(filename):
    """
    İşlenmiş dosyaları preview olarak göster
    """
    try:
        file_path = os.path.join(PROCESSED_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({
                'success': False,
                'error': 'Dosya bulunamadı'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Gunicorn için app seviyesinde model yükleme - timeout ile
import signal
import sys

def timeout_handler(signum, frame):
    print("⏰ Model loading timeout - 5 dakika aşıldı!")
    print("💡 Render.com memory/time limit - Lazy loading kullanılacak")
    raise TimeoutError("Model loading timeout")

def safe_init_removers():
    """Railway'de lazy loading kullan - memory tasarrufu"""
    global ultra_remover, advanced_remover
    
    print("🚀 Railway deployment - Lazy loading mode")
    print("💾 Memory optimization - Models loaded on demand")
    
    # Railway'de memory tasarrufu için lazy loading kullan
    ultra_remover = None
    advanced_remover = None
    print("✅ Lazy loading configured!")

# Railway için lazy loading
safe_init_removers()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"💡 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)