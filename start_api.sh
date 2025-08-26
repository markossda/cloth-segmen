#!/bin/bash

echo "🚀 API Server Başlatılıyor..."

# Sanal ortamı aktifleştir
if [ -d ".venv" ]; then
    echo "📂 Sanal ortam aktifleştiriliyor..."
    source .venv/bin/activate
else
    echo "❌ Sanal ortam bulunamadı! .venv klasörü yok."
    exit 1
fi

# Gereksinimleri kontrol et
echo "🔍 Gereksinimler kontrol ediliyor..."
python -c "import rembg, flask" 2>/dev/null || {
    echo "❌ Gerekli kütüphaneler yüklü değil!"
    echo "🔧 Yükleniyor..."
    pip install rembg flask flask-cors werkzeug pillow numpy opencv-python
}

# API sunucusunu başlat
echo "🌐 API Server başlatılıyor http://localhost:5001"
echo "📱 iOS projenden bu adrese istek atabilirsin!"
echo ""
echo "Endpoints:"
echo "  POST /api/remove-background (file upload)"
echo "  POST /api/remove-background-base64 (base64)"
echo "  GET /api/status (sunucu durumu)"
echo ""

python api_server.py
