#!/usr/bin/env python3
"""
Gelişmiş Kıyafet Arka Plan Kaldırıcı Demo
Boyut düzeltmeli ve optimizasyonlu
"""

from advanced_clothing_bg_remover import AdvancedClothingBgRemover
import os
from pathlib import Path

def demo_advanced():
    """
    Gelişmiş özelliklerin demo'su
    """
    print("🚀 Gelişmiş Kıyafet Arka Plan Kaldırıcı - Demo")
    print("=" * 50)
    
    # Remover'ı başlat
    remover = AdvancedClothingBgRemover()
    
    # Test görüntüsü ara
    test_images = [
        "input.jpg", "test.jpg", "shirt.jpg", "dress.jpg", 
        "clothing.jpg", "product.jpg", "tshirt.jpg", "kiyafet.jpg"
    ]
    
    current_dir = Path(".")
    found_images = []
    
    for img_name in test_images:
        img_path = current_dir / img_name
        if img_path.exists():
            found_images.append(str(img_path))
    
    if not found_images:
        print("❌ Test için görüntü dosyası bulunamadı.")
        print("\n📋 Kullanım kılavuzu:")
        print("1. Bir kıyafet görüntüsünü aşağıdaki isimlerden biriyle kaydedin:")
        print("   - input.jpg, test.jpg, shirt.jpg, tshirt.jpg")
        print("2. Demo'yu tekrar çalıştırın:")
        print("   ./start.sh advanced_demo.py")
        print("\n💡 Veya doğrudan kullanın:")
        print("   ./start.sh advanced_clothing_bg_remover.py DOSYA_ADI.jpg")
        return
    
    print(f"✅ {len(found_images)} test görüntüsü bulundu!")
    
    for img_path in found_images:
        print(f"\n{'='*60}")
        print(f"🖼️  İşleniyor: {os.path.basename(img_path)}")
        print(f"{'='*60}")
        
        try:
            # Önce görüntüyü analiz et
            print("\n📊 GÖRÜNTÜ ANALİZİ:")
            print("-" * 20)
            analysis = remover.analyze_image(img_path)
            
            if analysis:
                print(f"✅ Format: {analysis.get('format', 'Bilinmiyor')}")
                print(f"✅ Renk modu: {analysis.get('mode', 'Bilinmiyor')}")
                
                # İşlem seçenekleri belirle
                options = {
                    'preprocess': True,
                    'fix_positioning': True,
                    'center_vertically': False,  # Tişört için üstten boşluk
                    'enhance': True,
                    'create_variants': True,
                    'add_padding': True
                }
                
                print(f"\n⚙️  İŞLEM SEÇENEKLERİ:")
                print("-" * 20)
                for key, value in options.items():
                    status = "✅" if value else "❌"
                    print(f"{status} {key}: {value}")
                
                # Tam işlem yap
                result = remover.process_clothing_complete(img_path, options)
                
                if result:
                    print(f"\n🎉 BAŞARILI!")
                    print(f"📄 Ana dosya: {os.path.basename(result)}")
                    
                    # Oluşturulan dosyaları listele
                    result_dir = Path(result).parent
                    created_files = []
                    
                    # Ana dosya isimleri
                    base_name = Path(img_path).stem
                    possible_files = [
                        f"{base_name}_no_bg.png",
                        f"{base_name}_positioned.png", 
                        f"{base_name}_enhanced.png"
                    ]
                    
                    for file_name in possible_files:
                        file_path = result_dir / file_name
                        if file_path.exists():
                            created_files.append(file_name)
                    
                    # Varyant klasörünü kontrol et
                    variants_dir = result_dir / "variants"
                    if variants_dir.exists():
                        variant_files = list(variants_dir.glob(f"{base_name}_*.png"))
                        if variant_files:
                            created_files.append(f"variants/ ({len(variant_files)} dosya)")
                    
                    if created_files:
                        print(f"\n📁 Oluşturulan dosyalar:")
                        for file_name in created_files:
                            print(f"   • {file_name}")
                else:
                    print("❌ İşlem başarısız")
            else:
                print("❌ Görüntü analizi başarısız")
                
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
    
    print(f"\n🎊 Demo tamamlandı!")
    print("\n📋 Sonuç dosyaları:")
    print("• *_no_bg.png: Arka planı kaldırılmış")
    print("• *_positioned.png: Konumlandırılmış")
    print("• *_enhanced.png: E-ticaret için optimize edilmiş")
    print("• variants/: Farklı boyutlarda varyantlar")


def show_comparison():
    """
    Eski ve yeni versiyonun karşılaştırması
    """
    print("\n🔄 ESKİ vs YENİ VERSİYON KARŞILAŞTIRMASI")
    print("=" * 50)
    
    print("📊 clothing_bg_remover.py (Basit):")
    print("   ✅ Hızlı işlem")
    print("   ✅ Basit kullanım")
    print("   ❌ Boyut sorunları")
    print("   ❌ Konumlandırma sorunları")
    
    print("\n🚀 advanced_clothing_bg_remover.py (Gelişmiş):")
    print("   ✅ Boyut optimizasyonu")
    print("   ✅ Konumlandırma düzeltmesi")
    print("   ✅ E-ticaret iyileştirmesi")
    print("   ✅ Çoklu varyant oluşturma")
    print("   ✅ Görüntü analizi")
    print("   ❌ Biraz daha yavaş")
    
    print("\n💡 Öneri: Gelişmiş versiyonu kullanın!")


if __name__ == "__main__":
    demo_advanced()
    show_comparison()
    
    print(f"\n🔧 Manuel kullanım:")
    print(f"   ./start.sh advanced_clothing_bg_remover.py DOSYA.jpg")
    print(f"   ./start.sh advanced_clothing_bg_remover.py --analyze DOSYA.jpg")
    print(f"   ./start.sh advanced_clothing_bg_remover.py --folder ./klasor")
