#!/usr/bin/env python3
"""
Test script for clothing background remover
Bu script örnek kullanımları gösterir
"""

from clothing_bg_remover import ClothingBgRemover
import os
from pathlib import Path

def demo_usage():
    """
    Örnek kullanım senaryoları
    """
    print("🔧 Kıyafet Arka Plan Kaldırıcı - Demo")
    print("=" * 50)
    
    # Remover'ı başlat
    remover = ClothingBgRemover()
    
    # Test görüntüsü var mı kontrol et
    test_images = [
        "input.jpg", "test.jpg", "shirt.jpg", "dress.jpg", 
        "clothing.jpg", "product.jpg"
    ]
    
    current_dir = Path(".")
    found_images = []
    
    for img_name in test_images:
        img_path = current_dir / img_name
        if img_path.exists():
            found_images.append(str(img_path))
    
    if not found_images:
        print("❌ Test için görüntü dosyası bulunamadı.")
        print("\nKullanım örnekleri:")
        print("1. Bir kıyafet görüntüsünü 'input.jpg' olarak kaydedin")
        print("2. Scripti çalıştırın:")
        print("   python test_demo.py")
        print("\nVeya komut satırından doğrudan kullanın:")
        print("   python clothing_bg_remover.py input.jpg")
        return
    
    print(f"✅ {len(found_images)} test görüntüsü bulundu!")
    
    for img_path in found_images:
        print(f"\n🖼️  İşleniyor: {os.path.basename(img_path)}")
        print("-" * 30)
        
        try:
            # Tam işlem yap
            result = remover.process_image(
                img_path, 
                enhance=True,     # Vitrin iyileştirmesi
                add_shadow=False  # Gölge efekti (ağır işlem)
            )
            
            if result:
                print(f"✅ Başarılı: {os.path.basename(result)}")
            else:
                print("❌ İşlem başarısız")
                
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
    
    print(f"\n🎉 Demo tamamlandı!")
    print("\nOluşturulan dosyalar:")
    print("- *_no_bg.png: Arka planı kaldırılmış")
    print("- *_storefront.png: Vitrin görünümü")

def show_available_models():
    """
    Mevcut rembg modellerini göster
    """
    print("\n📋 Mevcut rembg modelleri:")
    print("-" * 30)
    
    models = [
        ("u2net", "Genel amaçlı, yüksek kalite"),
        ("u2net_human_seg", "İnsan segmentasyonu"),
        ("u2net_cloth_seg", "Kıyafet segmentasyonu ⭐"),
        ("isnet-general-use", "Genel kullanım"),
        ("silueta", "Siluet çıkarma"),
    ]
    
    for model, description in models:
        print(f"• {model}: {description}")
    
    print("\n⭐ Bu proje u2net_cloth_seg modelini kullanır")

if __name__ == "__main__":
    # Demo'yu çalıştır
    demo_usage()
    
    # Model bilgilerini göster
    show_available_models()
    
    print(f"\n💡 İpucu: Farklı modeller denemek için clothing_bg_remover.py dosyasında")
    print(f"   'u2net_cloth_seg' yerine başka model adı yazabilirsiniz.")
