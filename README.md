# Kıyafet Arka Plan Kaldırıcı

Bu proje, kıyafet görüntülerinin arka planını kaldırarak vitrin görünümü oluşturmak için geliştirilmiştir. `rembg` kütüphanesinin `u2net_cloth_seg` modelini kullanarak özellikle kıyafetler için optimize edilmiştir.

## Özellikler

- 🎯 **Kıyafet Odaklı**: u2net_cloth_seg modeli ile kıyafetler için optimize edilmiş arka plan kaldırma
- ✨ **Vitrin Görünümü**: Otomatik kontrast, parlaklık ve keskinlik iyileştirmesi
- 🌫️ **Gölge Efekti**: İsteğe bağlı doğal gölge efekti ekleme
- 📁 **Toplu İşlem**: Klasördeki tüm görüntüleri tek seferde işleme
- 🖼️ **Çoklu Format**: JPG, PNG, BMP, TIFF, WebP desteği

## Kurulum

```bash
# Sanal ortam oluştur (isteğe bağlı)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate     # Windows

# Gerekli paketleri yükle
pip install rembg pillow numpy opencv-python
```

## Kullanım

### Tek Dosya İşleme

```bash
# Basit kullanım
python clothing_bg_remover.py input.jpg

# Çıktı dosyası belirterek
python clothing_bg_remover.py input.jpg output.png
```

### Klasör İşleme

```bash
# Klasördeki tüm görüntüleri işle
python clothing_bg_remover.py --folder ./images
```

### Komut Satırı Örnekleri

```bash
# Tek bir kıyafet görüntüsü
python clothing_bg_remover.py shirt.jpg

# Belirli çıktı dosyası ile
python clothing_bg_remover.py dress.jpg clean_dress.png

# Toplu işlem
python clothing_bg_remover.py --folder ./product_photos
```

## Çıktı Dosyaları

Script aşağıdaki dosyaları oluşturur:

- `*_no_bg.png`: Arka planı kaldırılmış ham görüntü
- `*_storefront.png`: Vitrin görünümü için iyileştirilmiş görüntü
- `*_with_shadow.png`: Gölge efekti eklenmiş görüntü (isteğe bağlı)

## Özelleştirme

`ClothingBgRemover` sınıfını kullanarak kendi uygulamanızı oluşturabilirsiniz:

```python
from clothing_bg_remover import ClothingBgRemover

# Remover'ı başlat
remover = ClothingBgRemover()

# Sadece arka plan kaldır
remover.remove_background("input.jpg", "output.png")

# Tam işlem (arka plan + iyileştirme)
remover.process_image("input.jpg", enhance=True, add_shadow=True)

# Klasör işleme
remover.process_folder("./images", enhance=True, add_shadow=False)
```

## Model Bilgisi

Bu proje `u2net_cloth_seg` modelini kullanır:
- Kıyafetler için özel olarak eğitilmiş
- Yüksek kaliteli segmentasyon
- Kıyafet detaylarını korur
- Hızlı işlem süresi

## Desteklenen Formatlar

**Girdi**: JPG, JPEG, PNG, BMP, TIFF, WebP
**Çıktı**: PNG (şeffaflık desteği için)

## Gereksinimler

- Python 3.7+
- rembg
- Pillow (PIL)
- NumPy
- OpenCV (cv2)

## İpuçları

1. **En İyi Sonuçlar İçin**:
   - Yüksek çözünürlüklü görüntüler kullanın
   - Kıyafet ve arka plan arasında iyi kontrast olsun
   - Tek parça kıyafetler daha iyi sonuç verir

2. **Performans**:
   - İlk çalıştırmada model indirilir (~176MB)
   - GPU varsa daha hızlı işlem
   - Toplu işlemde bellek kullanımına dikkat edin

3. **Sorun Giderme**:
   - Düşük kaliteli sonuçlar için farklı modeller deneyin
   - Çok karmaşık arka planlar zorlu olabilir
   - Manuel düzeltme gerekebilir

## Lisans

Bu proje açık kaynak kodludur. Ticari kullanım için rembg lisansını kontrol edin.
