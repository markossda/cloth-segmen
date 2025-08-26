#!/usr/bin/env python3
"""
Batch processor for clothing images
Toplu kıyafet görüntüsü işleyici
"""

import os
import sys
from pathlib import Path
from clothing_bg_remover import ClothingBgRemover

def create_sample_structure():
    """
    Örnek klasör yapısı oluştur
    """
    folders = [
        "input_images",
        "processed_images", 
        "examples"
    ]
    
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"📁 Klasör oluşturuldu: {folder}")
    
    # README dosyası oluştur
    readme_content = """
# Klasör Yapısı

- `input_images/`: İşlenecek kıyafet görüntülerini buraya koyun
- `processed_images/`: İşlenmiş görüntüler burada saklanır
- `examples/`: Örnek görüntüler

## Kullanım

1. Kıyafet görüntülerini `input_images/` klasörüne koyun
2. Batch processor'ı çalıştırın:
   ```bash
   python batch_processor.py
   ```
"""
    
    with open("folder_structure.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📄 folder_structure.md oluşturuldu")

def batch_process():
    """
    Toplu işlem yap
    """
    input_folder = Path("input_images")
    output_folder = Path("processed_images")
    
    # Klasörler var mı kontrol et
    if not input_folder.exists():
        print("❌ input_images klasörü bulunamadı!")
        print("📁 Klasör yapısını oluşturuyor...")
        create_sample_structure()
        print("\n✅ Kıyafet görüntülerini input_images/ klasörüne koyup tekrar çalıştırın.")
        return
    
    # Çıktı klasörünü oluştur
    output_folder.mkdir(exist_ok=True)
    
    # Desteklenen formatlar
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # Görüntü dosyalarını bul
    image_files = [
        f for f in input_folder.iterdir() 
        if f.is_file() and f.suffix.lower() in supported_formats
    ]
    
    if not image_files:
        print(f"❌ {input_folder} klasöründe görüntü dosyası bulunamadı!")
        print("📝 Desteklenen formatlar: JPG, PNG, BMP, TIFF, WebP")
        return
    
    print(f"🔍 {len(image_files)} görüntü dosyası bulundu")
    print(f"📂 Çıktı klasörü: {output_folder}")
    
    # İşleme seçenekleri
    print("\n⚙️  İşlem seçenekleri:")
    print("1. Sadece arka plan kaldır")
    print("2. Arka plan kaldır + vitrin iyileştirmesi")
    print("3. Tam işlem (arka plan + iyileştirme + gölge)")
    
    try:
        choice = input("\nSeçiminiz (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n❌ İşlem iptal edildi")
        return
    
    enhance = choice in ['2', '3']
    add_shadow = choice == '3'
    
    # Remover'ı başlat
    remover = ClothingBgRemover()
    
    success_count = 0
    
    print(f"\n🚀 İşlem başlıyor...")
    print("=" * 50)
    
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] {image_file.name}")
        
        try:
            # İşle
            result = remover.process_image(
                str(image_file),
                enhance=enhance,
                add_shadow=add_shadow
            )
            
            if result:
                # İşlenmiş dosyayı output klasörüne taşı
                result_file = Path(result)
                new_path = output_folder / result_file.name
                
                if result_file.exists():
                    result_file.rename(new_path)
                    print(f"✅ Kaydedildi: {new_path}")
                    success_count += 1
                else:
                    print("❌ Sonuç dosyası bulunamadı")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
    
    print(f"\n🎉 İşlem tamamlandı!")
    print(f"✅ Başarılı: {success_count}/{len(image_files)}")
    print(f"📂 Çıktı klasörü: {output_folder}")

def main():
    """
    Ana fonksiyon
    """
    print("👕 Kıyafet Arka Plan Kaldırıcı - Toplu İşlem")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        create_sample_structure()
        return
    
    batch_process()

if __name__ == "__main__":
    main()
