#!/bin/bash
# Hızlı başlangıç scripti - rembg projesini çalıştırmak için

echo "🔧 Kıyafet Arka Plan Kaldırıcı - Hızlı Başlangıç"
echo "================================================"

# Sanal ortamı kontrol et
if [ ! -d ".venv" ]; then
    echo "❌ Sanal ortam bulunamadı!"
    echo "💡 Önce python -m venv .venv komutu ile sanal ortam oluşturun"
    exit 1
fi

# Sanal ortamı aktifleştir
echo "🔄 Sanal ortam aktifleştiriliyor..."
source .venv/bin/activate

# Python ve paketleri kontrol et
echo "✅ Python versiyonu: $(python --version)"

# rembg paketini kontrol et
if ! python -c "import rembg" 2>/dev/null; then
    echo "❌ rembg paketi bulunamadı!"
    echo "📦 Paketler yükleniyor..."
    pip install -r requirements.txt
fi

echo "✅ Tüm paketler hazır!"
echo ""

# Kullanım örnekleri göster
echo "📋 Kullanım örnekleri:"
echo "----------------------"
echo "# Basit işlem:"
echo "python clothing_bg_remover.py kiyafet.jpg"
echo ""
echo "# Gelişmiş işlem (boyut düzeltmeli):"
echo "python advanced_clothing_bg_remover.py kiyafet.jpg"
echo ""
echo "# Toplu işlem:"
echo "python clothing_bg_remover.py --folder ./resimler"
echo ""
echo "# Görüntü analizi:"
echo "python advanced_clothing_bg_remover.py --analyze kiyafet.jpg"
echo ""
echo "# Demo çalıştır:"
echo "python test_demo.py"
echo ""
echo "# Batch processor:"
echo "python batch_processor.py"
echo ""

# Eğer parametre verilmişse çalıştır
if [ $# -gt 0 ]; then
    echo "🚀 Komut çalıştırılıyor: python $@"
    python "$@"
else
    echo "💡 Kullanım: ./start.sh [komut ve parametreler]"
    echo "   Örnek: ./start.sh clothing_bg_remover.py test.jpg"
fi
