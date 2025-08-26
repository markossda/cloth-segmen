# 👕 Kıyafet Arka Plan Kaldırıcı - Hızlı Kullanım Kılavuzu

## 🚀 En Kolay Yöntem

**Hiç uğraşmak istemiyorsan, sadece şunu çalıştır:**

```bash
# Basit işlem:
./start.sh clothing_bg_remover.py kiyafet.jpg

# GELİŞMİŞ İŞLEM (boyut düzeltmeli) - ÖNERİLEN:
./start.sh advanced_clothing_bg_remover.py kiyafet.jpg

# Gelişmiş demo:
./start.sh advanced_demo.py
```

## 🚀 Manuel Yöntem

### Önemli: Sanal Ortamı Aktifleştirin
```bash
# Önce sanal ortamı aktifleştirin
source .venv/bin/activate

# Veya doğrudan tam yol kullanın
./.venv/bin/python clothing_bg_remover.py kiyafet.jpg
```

### 1. Tek Dosya İşleme
```bash
# Sanal ortam aktifse:
python clothing_bg_remover.py kiyafet.jpg

# Veya tam yol ile:
./.venv/bin/python clothing_bg_remover.py kiyafet.jpg

# Belirli çıktı dosyası ile
./.venv/bin/python clothing_bg_remover.py kiyafet.jpg temiz_kiyafet.png
```

### 2. Toplu İşlem
```bash
# Klasördeki tüm görüntüleri işle
./.venv/bin/python clothing_bg_remover.py --folder ./kiyafet_resimleri

# Veya batch processor kullan
./.venv/bin/python batch_processor.py
```

## 📂 Dosya Yapısı

```
rempbg/
├── clothing_bg_remover.py    # Ana script
├── batch_processor.py        # Toplu işlem
├── test_demo.py             # Demo ve test
├── requirements.txt         # Gerekli paketler
├── config.json             # Ayarlar
└── README.md               # Detaylı dokümantasyon
```

## ⚡ Hızlı Test

⚠️ **ÖNEMLİ: Her zaman sanal ortamı aktifleştirin!**

```bash
# ÖNCE SANAL ORTAMI AKTİFLEŞTİR
source .venv/bin/activate
```

1. Bir kıyafet fotoğrafını `input.jpg` olarak kaydedin
2. Demo'yu çalıştırın:
   ```bash
   # Sanal ortam aktifleştirildikten sonra:
   python test_demo.py
   
   # Veya doğrudan tam yol ile:
   ./.venv/bin/python test_demo.py
   ```

## 🎯 Özellikler

- ✅ **u2net_cloth_seg** modeli ile kıyafet odaklı işlem
- ✅ Otomatik arka plan kaldırma
- ✅ Vitrin görünümü iyileştirmesi
- ✅ Toplu işlem desteği
- ✅ Gölge efekti (isteğe bağlı)

## 📋 Çıktı Dosyaları

- `*_no_bg.png` - Arka planı kaldırılmış
- `*_storefront.png` - Vitrin görünümü
- `*_with_shadow.png` - Gölge efektli

## 🛠 Sorun Giderme

**Model indirilemiyorsa:**
```bash
pip install --upgrade rembg onnxruntime
```

**Görüntü işlenemiyorsa:**
- Dosya formatını kontrol edin (JPG, PNG desteklenir)
- Dosya yolunu kontrol edin
- Görüntü çözünürlüğünü kontrol edin

## 💡 İpuçları

1. **En iyi sonuçlar için:**
   - Yüksek çözünürlük kullanın
   - İyi kontrast olan görüntüler seçin
   - Düz arka plan tercih edin

2. **Performans:**
   - İlk çalıştırmada model indirilir (~176MB)
   - GPU varsa daha hızlı çalışır

3. **Özelleştirme:**
   - `config.json` dosyasından ayarları değiştirin
   - Farklı modeller için kod içinde `u2net_cloth_seg` yerine başka model adı yazın

## 🔧 Komut Örnekleri

⚠️ **Dikkat: Sanal ortamı aktifleştirmeyi unutma!**

```bash
# İlk önce sanal ortamı aktifleştir
source .venv/bin/activate

# Sonra komutları çalıştır:
python clothing_bg_remover.py gomlek.jpg
python clothing_bg_remover.py elbise.jpg temiz_elbise.png
python clothing_bg_remover.py --folder ./urunler

# Veya direkt tam yol ile (sanal ortam gerekmez):
./.venv/bin/python clothing_bg_remover.py gomlek.jpg
./.venv/bin/python clothing_bg_remover.py elbise.jpg temiz_elbise.png  
./.venv/bin/python clothing_bg_remover.py --folder ./urunler

# Batch processor
./.venv/bin/python batch_processor.py --setup  # Klasör yapısı oluştur
./.venv/bin/python batch_processor.py          # İşlemi başlat
```

## 📞 Yardım

Daha fazla bilgi için `README.md` dosyasını okuyun veya demo scripti çalıştırın:
```bash
python test_demo.py
```
