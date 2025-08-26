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

# Global remover'lar (bir kez yüklensin)
ultra_remover = None
advanced_remover = None

def init_removers():
    """
    Remover'ları başlat
    """
    global ultra_remover, advanced_remover
    try:
        print("🤖 AI modelleri yükleniyor...")
        ultra_remover = UltraClothingBgRemover()
        advanced_remover = AdvancedClothingBgRemover('u2net_cloth_seg')
        print("✅ AI modelleri hazır!")
    except Exception as e:
        print(f"❌ Model yükleme hatası: {e}")

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
    Server sağlık kontrolü
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'models_loaded': ultra_remover is not None and advanced_remover is not None,
        'memory_usage': os.popen('ps -o rss= -p %d' % os.getpid()).read().strip(),
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
        status['ultra_model'] = ultra_remover.best_model
    if advanced_remover:
        status['advanced_model'] = advanced_remover.model_name
    
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
            result_path = ultra_remover.ultra_process(filepath, options)
            used_model = ultra_remover.best_model
            
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
            result_path = advanced_remover.process_clothing_complete(filepath, options)
            used_model = advanced_remover.model_name
        
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
            result_path = ultra_remover.ultra_process(filepath, options)
            used_model = ultra_remover.best_model
        else:
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
    docs = """
    <h1>🚀 Kıyafet Arka Plan Kaldırıcı API</h1>
    
    <h2>📡 Endpoint'ler:</h2>
    
    <h3>GET /health</h3>
    <p>Server durumu kontrolü</p>
    
    <h3>GET /api/models</h3>
    <p>Mevcut AI modellerini listele</p>
    
    <h3>POST /api/remove-background</h3>
    <p>Arka plan kaldırma (multipart/form-data)</p>
    <p><strong>Parametreler:</strong></p>
    <ul>
        <li>image: Görüntü dosyası</li>
        <li>model: ultra|advanced (default: ultra)</li>
        <li>positioning: smart|center (default: smart)</li>
        <li>variants: true|false (default: true)</li>
        <li>enhance: true|false (default: true)</li>
    </ul>
    
    <h3>POST /api/remove-background-base64</h3>
    <p>Base64 formatında arka plan kaldırma (iOS için)</p>
    <p><strong>JSON Parametreler:</strong></p>
    <ul>
        <li>image_base64: Base64 encoded görüntü</li>
        <li>model: ultra|advanced</li>
        <li>positioning: smart|center</li>
    </ul>
    
    <h3>GET /api/download/&lt;filename&gt;</h3>
    <p>İşlenmiş dosyaları indir</p>
    
    <h3>GET /api/preview/&lt;filename&gt;</h3>
    <p>İşlenmiş dosyaları görüntüle</p>
    
    <h2>🤖 AI Modeller:</h2>
    <ul>
        <li><strong>ULTRA:</strong> En gelişmiş AI modelleri (isnet-general-use, sam)</li>
        <li><strong>Advanced:</strong> Boyut düzeltmeli model (u2net_cloth_seg)</li>
    </ul>
    
    <h2>📱 iOS Kullanım Örneği:</h2>
    <pre>
    curl -X POST http://localhost:5001/api/remove-background-base64 \\
         -H "Content-Type: application/json" \\
         -d '{"image_base64": "iVBORw0KGgoAAAANS...", "model": "ultra", "positioning": "smart"}'
    </pre>
    """
    return docs

if __name__ == '__main__':
    # Başlangıçta modelleri yükle
    init_removers()
    port = int(os.environ.get('PORT', 8080))
    print(f"💡 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port)
