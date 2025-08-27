#!/usr/bin/env python3
"""
Kıyafet Arka Plan Kaldırıcı - Web API Server
iOS projesi için REST API endpoint'leri
"""

from flask import Flask, request, jsonify, send_file, render_template_string
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

# HTML template'i
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Kıyafet Arka Plan Kaldırıcı API</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            line-height: 1.6; 
            padding: 2em; 
            max-width: 800px; 
            margin: 0 auto;
            color: #333;
        }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; margin-top: 1.5em; }
        pre { 
            background: #f8f9fa; 
            padding: 1em; 
            border-radius: 4px; 
            overflow-x: auto;
            border: 1px solid #e9ecef;
        }
        .endpoint { 
            background: #fff; 
            padding: 1em; 
            margin: 1em 0; 
            border-radius: 4px; 
            border: 1px solid #e9ecef;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .method { 
            font-weight: bold; 
            color: #2ecc71; 
            background: #f1f9f1;
            padding: 0.2em 0.5em;
            border-radius: 3px;
        }
        .url { color: #3498db; }
        .param { margin-left: 1em; }
        .example { margin-top: 1em; }
        .note { 
            background: #fff3cd; 
            padding: 1em; 
            border-radius: 4px; 
            margin: 1em 0;
            border: 1px solid #ffeeba;
        }
        code {
            background: #f8f9fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>🚀 Kıyafet Arka Plan Kaldırıcı API</h1>
    
    <div class="note">
        <strong>Not:</strong> Bu bir RESTful API servisidir. Kullanım için HTTP istekleri yapmanız gerekir.
    </div>

    <h2>📡 Endpoints</h2>

    <div class="endpoint">
        <h3>Sağlık Kontrolü</h3>
        <p><span class="method">GET</span> <span class="url">/health</span></p>
        <div class="example">
            <strong>Örnek:</strong>
            <pre>curl https://cloth-segmentation-api.onrender.com/health</pre>
        </div>
    </div>

    <div class="endpoint">
        <h3>Arka Plan Kaldırma (Form Data)</h3>
        <p><span class="method">POST</span> <span class="url">/api/remove-background</span></p>
        <p>Parametreler:</p>
        <div class="param">
            <code>image</code>: Görüntü dosyası (PNG, JPG)<br>
            <code>model</code>: ultra veya advanced (varsayılan: ultra)<br>
            <code>positioning</code>: smart veya center (varsayılan: smart)<br>
            <code>enhance</code>: true veya false (varsayılan: false)
        </div>
        <div class="example">
            <strong>Örnek:</strong>
            <pre>curl -X POST https://cloth-segmentation-api.onrender.com/api/remove-background \\
-F "image=@image.jpg" \\
-F "model=ultra" \\
-F "positioning=smart"</pre>
        </div>
    </div>

    <div class="endpoint">
        <h3>Arka Plan Kaldırma (Base64)</h3>
        <p><span class="method">POST</span> <span class="url">/api/remove-background-base64</span></p>
        <p>JSON Parametreler:</p>
        <div class="param">
            <code>image_base64</code>: Base64 encoded görüntü<br>
            <code>model</code>: ultra veya advanced<br>
            <code>positioning</code>: smart veya center
        </div>
        <div class="example">
            <strong>Örnek:</strong>
            <pre>curl -X POST https://cloth-segmentation-api.onrender.com/api/remove-background-base64 \\
-H "Content-Type: application/json" \\
-d '{"image_base64": "BASE64_IMAGE_DATA", "model": "ultra"}'</pre>
        </div>
    </div>

    <h2>📱 Swift Örnek Kod</h2>
    <pre>
let url = URL(string: "https://cloth-segmentation-api.onrender.com/api/remove-background-base64")!
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
}.resume()</pre>

</body>
</html>
"""

# Kendi modüllerimizi import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ultra_clothing_bg_remover import UltraClothingBgRemover
from advanced_clothing_bg_remover import AdvancedClothingBgRemover

app = Flask(__name__)
CORS(app)  # iOS'tan istek gelebilsin

# Konfigürasyon
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Klasörleri oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Global remover'lar (lazy loading)
ultra_remover = None
advanced_remover = None

def get_ultra_remover():
    """
    Ultra remover'ı lazy loading ile al
    """
    global ultra_remover
    if ultra_remover is None:
        print("🤖 Ultra AI modeli yükleniyor...")
        ultra_remover = UltraClothingBgRemover()
        print("✅ Ultra AI modeli hazır!")
    return ultra_remover

def get_advanced_remover():
    """
    Advanced remover'ı lazy loading ile al
    """
    global advanced_remover
    if advanced_remover is None:
        print("🤖 Advanced AI modeli yükleniyor...")
        advanced_remover = AdvancedClothingBgRemover('u2net_cloth_seg')
        print("✅ Advanced AI modeli hazır!")
    return advanced_remover

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

@app.route('/health', methods=['GET'])
def health_check():
    """
    Server sağlık kontrolü - hızlı yanıt için basit tutuldu
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0',
        'ready': True
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
    
    try:
        status['ultra_model'] = get_ultra_remover().best_model
    except:
        status['ultra_model'] = 'not_loaded'
    
    try:
        status['advanced_model'] = get_advanced_remover().model_name
    except:
        status['advanced_model'] = 'not_loaded'
    
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
        model_type = request.form.get('model', 'ultra')  # ultra veya advanced
        positioning = request.form.get('positioning', 'smart')  # smart veya center
        create_variants = request.form.get('variants', 'true').lower() == 'true'
        enhance = request.form.get('enhance', 'false').lower() == 'true'  # Şeffaf PNG için false
        
        # Dosyayı kaydet
        filename = generate_unique_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        print(f"📁 Dosya kaydedildi: {filename}")
        print(f"⚙️  Parametreler: model={model_type}, positioning={positioning}")
        
        start_time = time.time()
        
        # Model seçimi ve işlem
        if model_type == 'ultra' and ultra_remover:
            options = {
                'ai_positioning': True,
                'enhance': enhance,
                'create_variants': create_variants,
                'positioning_mode': positioning
            }
            remover = get_ultra_remover()
            result_path = remover.ultra_process(filepath, options)
            used_model = remover.best_model
            
        else:
            # Advanced model kullan
            options = {
                'preprocess': True,
                'fix_positioning': True,
                'center_vertically': positioning == 'center',
                'enhance': enhance,
                'create_variants': create_variants,
                'add_padding': True
            }
            remover = get_advanced_remover()
            result_path = remover.process_clothing_complete(filepath, options)
            used_model = remover.model_name
        
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
        
        # Varyantları kontrol et
        variants_info = []
        variants_dir = Path(result_path).parent / "variants"
        ultra_variants_dir = Path(result_path).parent / "ultra_variants"
        
        for var_dir in [variants_dir, ultra_variants_dir]:
            if var_dir.exists():
                base_name = Path(filepath).stem
                variant_files = list(var_dir.glob(f"*{base_name}*.png"))
                for variant_file in variant_files:
                    # Varyantı da processed'a taşı
                    var_final_path = os.path.join(PROCESSED_FOLDER, variant_file.name)
                    os.rename(str(variant_file), var_final_path)
                    
                    file_size = os.path.getsize(var_final_path)
                    variants_info.append({
                        'filename': variant_file.name,
                        'size_bytes': file_size,
                        'download_url': f'/api/download/{variant_file.name}'
                    })
        
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
            'variants': variants_info,
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

@app.route('/api/remove-background-base64', methods=['POST'])
def remove_background_base64():
    """
    Base64 formatında görüntü işleme (iOS için alternatif)
    """
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
        enhance = data.get('enhance', False)  # Şeffaf PNG için false
        create_variants = data.get('create_variants', False)
        
        print(f"📱 Base64 işlem: model={model_type}, positioning={positioning}")
        
        start_time = time.time()
        
        # İşlem
        if model_type == 'ultra' and ultra_remover:
            options = {
                'ai_positioning': True,
                'enhance': enhance,
                'create_variants': create_variants,
                'positioning_mode': positioning
            }
            remover = get_ultra_remover()
            result_path = remover.ultra_process(filepath, options)
            used_model = remover.best_model
        else:
            options = {
                'preprocess': True,
                'fix_positioning': True,
                'center_vertically': positioning == 'center',
                'enhance': enhance,
                'create_variants': create_variants,
                'add_padding': True
            }
            remover = get_advanced_remover()
            result_path = remover.process_clothing_complete(filepath, options)
            used_model = remover.model_name
        
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

@app.route('/', methods=['GET'])
def index():
    """
    Ana sayfa - API dokümantasyonu
    """
    return render_template_string(INDEX_HTML)
<!DOCTYPE html>
<html>
<head>
    <title>Kıyafet Arka Plan Kaldırıcı API</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            line-height: 1.6; 
            padding: 2em; 
            max-width: 800px; 
            margin: 0 auto;
            color: #333;
        }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; margin-top: 1.5em; }
        pre { 
            background: #f8f9fa; 
            padding: 1em; 
            border-radius: 4px; 
            overflow-x: auto;
            border: 1px solid #e9ecef;
        }
        .endpoint { 
            background: #fff; 
            padding: 1em; 
            margin: 1em 0; 
            border-radius: 4px; 
            border: 1px solid #e9ecef;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .method { 
            font-weight: bold; 
            color: #2ecc71; 
            background: #f1f9f1;
            padding: 0.2em 0.5em;
            border-radius: 3px;
        }
        .url { color: #3498db; }
        .param { margin-left: 1em; }
        .example { margin-top: 1em; }
        .note { 
            background: #fff3cd; 
            padding: 1em; 
            border-radius: 4px; 
            margin: 1em 0;
            border: 1px solid #ffeeba;
        }
        code {
            background: #f8f9fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>🚀 Kıyafet Arka Plan Kaldırıcı API</h1>
    
    <div class="note">
        <strong>Not:</strong> Bu bir RESTful API servisidir. Kullanım için HTTP istekleri yapmanız gerekir.
    </div>

    <h2>📡 Endpoints</h2>

    <div class="endpoint">
        <h3>Sağlık Kontrolü</h3>
        <p><span class="method">GET</span> <span class="url">/health</span></p>
        <div class="example">
            <strong>Örnek:</strong>
            <pre>curl https://cloth-segmentation-api.onrender.com/health</pre>
        </div>
    </div>

    <div class="endpoint">
        <h3>Arka Plan Kaldırma (Form Data)</h3>
        <p><span class="method">POST</span> <span class="url">/api/remove-background</span></p>
        <p>Parametreler:</p>
        <div class="param">
            <code>image</code>: Görüntü dosyası (PNG, JPG)<br>
            <code>model</code>: ultra veya advanced (varsayılan: ultra)<br>
            <code>positioning</code>: smart veya center (varsayılan: smart)<br>
            <code>enhance</code>: true veya false (varsayılan: false)
        </div>
        <div class="example">
            <strong>Örnek:</strong>
            <pre>curl -X POST https://cloth-segmentation-api.onrender.com/api/remove-background \\
-F "image=@image.jpg" \\
-F "model=ultra" \\
-F "positioning=smart"</pre>
        </div>
    </div>

    <div class="endpoint">
        <h3>Arka Plan Kaldırma (Base64)</h3>
        <p><span class="method">POST</span> <span class="url">/api/remove-background-base64</span></p>
        <p>JSON Parametreler:</p>
        <div class="param">
            <code>image_base64</code>: Base64 encoded görüntü<br>
            <code>model</code>: ultra veya advanced<br>
            <code>positioning</code>: smart veya center
        </div>
        <div class="example">
            <strong>Örnek:</strong>
            <pre>curl -X POST https://cloth-segmentation-api.onrender.com/api/remove-background-base64 \\
-H "Content-Type: application/json" \\
-d '{"image_base64": "BASE64_IMAGE_DATA", "model": "ultra"}'</pre>
        </div>
    </div>

    <h2>📱 Swift Örnek Kod</h2>
    <pre>
let url = URL(string: "https://cloth-segmentation-api.onrender.com/api/remove-background-base64")!
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
}.resume()</pre>

</body>
</html>
'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kıyafet Arka Plan Kaldırıcı API</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; padding: 2em; max-width: 800px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            h2 { color: #34495e; margin-top: 1.5em; }
            pre { background: #f8f9fa; padding: 1em; border-radius: 4px; overflow-x: auto; }
            .endpoint { background: #fff; padding: 1em; margin: 1em 0; border-radius: 4px; border: 1px solid #e9ecef; }
            .method { font-weight: bold; color: #2ecc71; }
            .url { color: #3498db; }
            .param { margin-left: 1em; }
            .example { margin-top: 1em; }
            .note { background: #fff3cd; padding: 1em; border-radius: 4px; margin: 1em 0; }
        </style>
    </head>
    <body>
        <h1>🚀 Kıyafet Arka Plan Kaldırıcı API</h1>
        
        <div class="note">
            <strong>Not:</strong> Bu bir RESTful API servisidir. Kullanım için HTTP istekleri yapmanız gerekir.
        </div>

        <h2>📡 Endpoints</h2>

        <div class="endpoint">
            <h3>Sağlık Kontrolü</h3>
            <p><span class="method">GET</span> <span class="url">/health</span></p>
            <div class="example">
                <strong>Örnek:</strong>
                <pre>curl https://cloth-segmentation-api.onrender.com/health</pre>
            </div>
        </div>

        <div class="endpoint">
            <h3>Arka Plan Kaldırma (Form Data)</h3>
            <p><span class="method">POST</span> <span class="url">/api/remove-background</span></p>
            <p>Parametreler:</p>
            <div class="param">
                <code>image</code>: Görüntü dosyası (PNG, JPG)<br>
                <code>model</code>: ultra veya advanced (varsayılan: ultra)<br>
                <code>positioning</code>: smart veya center (varsayılan: smart)<br>
                <code>enhance</code>: true veya false (varsayılan: false)
            </div>
            <div class="example">
                <strong>Örnek:</strong>
                <pre>curl -X POST https://cloth-segmentation-api.onrender.com/api/remove-background \\
    -F "image=@image.jpg" \\
    -F "model=ultra" \\
    -F "positioning=smart"</pre>
            </div>
        </div>

        <div class="endpoint">
            <h3>Arka Plan Kaldırma (Base64)</h3>
            <p><span class="method">POST</span> <span class="url">/api/remove-background-base64</span></p>
            <p>JSON Parametreler:</p>
            <div class="param">
                <code>image_base64</code>: Base64 encoded görüntü<br>
                <code>model</code>: ultra veya advanced<br>
                <code>positioning</code>: smart veya center
            </div>
            <div class="example">
                <strong>Örnek:</strong>
                <pre>curl -X POST https://cloth-segmentation-api.onrender.com/api/remove-background-base64 \\
    -H "Content-Type: application/json" \\
    -d '{"image_base64": "BASE64_IMAGE_DATA", "model": "ultra"}'</pre>
            </div>
        </div>

        <h2>📱 Swift Örnek Kod</h2>
        <pre>
let url = URL(string: "https://cloth-segmentation-api.onrender.com/api/remove-background-base64")!
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
}.resume()</pre>

    </body>
    </html>
    """
    return docs_html
            '/api/remove-background': {
                'method': 'POST',
                'description': 'Görüntünün arka planını kaldır (multipart/form-data)',
                'parameters': {
                    'image': 'Görüntü dosyası (PNG, JPG)',
                    'model': 'ultra veya advanced (varsayılan: ultra)',
                    'positioning': 'smart veya center (varsayılan: smart)',
                    'enhance': 'true veya false (varsayılan: false)'
                },
                'example': """
                curl -X POST https://cloth-segmentation-api.onrender.com/api/remove-background \\
                  -F "image=@image.jpg" \\
                  -F "model=ultra" \\
                  -F "positioning=smart"
                """
            },
            '/api/remove-background-base64': {
                'method': 'POST',
                'description': 'Base64 formatında görüntünün arka planını kaldır (iOS için)',
                'parameters': {
                    'image_base64': 'Base64 encoded görüntü',
                    'model': 'ultra veya advanced',
                    'positioning': 'smart veya center'
                },
                'example': """
                curl -X POST https://cloth-segmentation-api.onrender.com/api/remove-background-base64 \\
                  -H "Content-Type: application/json" \\
                  -d '{"image_base64": "BASE64_IMAGE_DATA", "model": "ultra"}'
                """
            }
        },
        'swift_example': """
        // Swift örnek kod
        let url = URL(string: "https://cloth-segmentation-api.onrender.com/api/remove-background-base64")!
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
            // Handle response
        }.resume()
        """
    }
    return jsonify(docs)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Server starting on port {port}")
    print("💡 AI modeller ilk kullanımda yüklenecek (lazy loading)")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

