#!/usr/bin/env python3
"""
Clothing Background Remover
Bu script kıyafet görüntülerinin arka planını kaldırır ve vitrin görünümü oluşturur.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np
from rembg import remove, new_session
import cv2

class ClothingBgRemover:
    def __init__(self):
        # u2net_cloth_seg modeli özellikle kıyafetler için optimize edilmiştir
        self.session = new_session('u2net_cloth_seg')
        
    def remove_background(self, input_path, output_path=None):
        """
        Kıyafet görüntüsünün arka planını kaldırır
        """
        try:
            # Girdi dosyasını kontrol et
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Girdi dosyası bulunamadı: {input_path}")
            
            # Çıktı dosyası yolu oluştur
            if output_path is None:
                input_file = Path(input_path)
                output_path = input_file.parent / f"{input_file.stem}_no_bg.png"
            
            print(f"İşleniyor: {input_path}")
            
            # Görüntüyü yükle
            with open(input_path, 'rb') as input_file:
                input_data = input_file.read()
            
            # Arka planı kaldır
            output_data = remove(input_data, session=self.session)
            
            # Sonucu kaydet
            with open(output_path, 'wb') as output_file:
                output_file.write(output_data)
            
            print(f"Başarıyla kaydedildi: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Hata: {str(e)}")
            return None
    
    def enhance_for_storefront(self, image_path, output_path=None):
        """
        Vitrin görünümü için görüntüyü iyileştir
        """
        try:
            # Görüntüyü yükle
            img = Image.open(image_path).convert("RGBA")
            
            # Kontrast ve parlaklığı artır
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)  # Kontrast %20 artır
            
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)  # Parlaklık %10 artır
            
            # Keskinliği artır
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.15)  # Keskinlik %15 artır
            
            # Çıktı dosyası yolu oluştur
            if output_path is None:
                input_file = Path(image_path)
                output_path = input_file.parent / f"{input_file.stem}_storefront.png"
            
            # Kaydet
            img.save(output_path, "PNG")
            print(f"Vitrin görünümü kaydedildi: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"İyileştirme hatası: {str(e)}")
            return None
    
    def add_shadow(self, image_path, output_path=None):
        """
        Görüntüye doğal gölge efekti ekle
        """
        try:
            # Görüntüyü yükle
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                raise ValueError("Görüntü yüklenemedi")
            
            h, w = img.shape[:2]
            
            # Gölge için yeni canvas oluştur
            shadow_canvas = np.zeros((h + 20, w + 20, 4), dtype=np.uint8)
            
            # Gölge efekti oluştur
            if img.shape[2] == 4:  # RGBA
                alpha = img[:, :, 3]
                shadow = np.zeros_like(alpha)
                shadow[alpha > 0] = 100  # Gölge yoğunluğu
                
                # Gölgeyi bulanıklaştır
                shadow = cv2.GaussianBlur(shadow, (15, 15), 0)
                
                # Gölgeyi konumlandır (sağa ve aşağıya kaydır)
                shadow_canvas[15:h+15, 15:w+15, 3] = shadow
                shadow_canvas[15:h+15, 15:w+15, 0] = 0  # Siyah gölge
                shadow_canvas[15:h+15, 15:w+15, 1] = 0
                shadow_canvas[15:h+15, 15:w+15, 2] = 0
                
                # Orijinal görüntüyü üste yerleştir
                shadow_canvas[10:h+10, 10:w+10] = cv2.addWeighted(
                    shadow_canvas[10:h+10, 10:w+10], 0.7, 
                    np.pad(img, ((0, 0), (0, 0), (0, 0)), mode='constant'), 1.0, 0
                )
            
            # Çıktı dosyası yolu oluştur
            if output_path is None:
                input_file = Path(image_path)
                output_path = input_file.parent / f"{input_file.stem}_with_shadow.png"
            
            # Kaydet
            cv2.imwrite(str(output_path), shadow_canvas)
            print(f"Gölge efekti eklendi: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Gölge ekleme hatası: {str(e)}")
            return None
    
    def process_image(self, input_path, enhance=True, add_shadow=False):
        """
        Tam işlem: arka plan kaldırma + vitrin iyileştirmesi
        """
        print(f"\n{'='*50}")
        print(f"İşleniyor: {os.path.basename(input_path)}")
        print(f"{'='*50}")
        
        # 1. Arka planı kaldır
        no_bg_path = self.remove_background(input_path)
        if not no_bg_path:
            return None
        
        current_path = no_bg_path
        
        # 2. Vitrin görünümü için iyileştir
        if enhance:
            enhanced_path = self.enhance_for_storefront(current_path)
            if enhanced_path:
                current_path = enhanced_path
        
        # 3. Gölge ekle (isteğe bağlı)
        if add_shadow:
            shadow_path = self.add_shadow(current_path)
            if shadow_path:
                current_path = shadow_path
        
        return current_path
    
    def process_folder(self, folder_path, enhance=True, add_shadow=False):
        """
        Klasördeki tüm görüntüleri işle
        """
        folder = Path(folder_path)
        if not folder.exists():
            print(f"Klasör bulunamadı: {folder_path}")
            return
        
        # Desteklenen dosya formatları
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        image_files = [
            f for f in folder.iterdir() 
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        
        if not image_files:
            print("Klasörde desteklenen görüntü dosyası bulunamadı.")
            return
        
        print(f"\n{len(image_files)} görüntü dosyası bulundu.")
        
        for image_file in image_files:
            self.process_image(str(image_file), enhance=enhance, add_shadow=add_shadow)
        
        print(f"\n✅ Tüm işlemler tamamlandı!")


def main():
    """
    Ana fonksiyon - komut satırı arayüzü
    """
    if len(sys.argv) < 2:
        print("""
Kullanım:
  python clothing_bg_remover.py <girdi_dosyası> [çıktı_dosyası]
  python clothing_bg_remover.py --folder <klasör_yolu>
  
Örnekler:
  python clothing_bg_remover.py input.jpg
  python clothing_bg_remover.py input.jpg output.png
  python clothing_bg_remover.py --folder ./images
  
Özellikler:
  - u2net_cloth_seg modeli ile kıyafet arka planı kaldırma
  - Vitrin görünümü için otomatik iyileştirme
  - Toplu işlem desteği
        """)
        return
    
    remover = ClothingBgRemover()
    
    if sys.argv[1] == "--folder":
        if len(sys.argv) < 3:
            print("Klasör yolu belirtiniz.")
            return
        
        folder_path = sys.argv[2]
        print("Gölge efekti eklensin mi? (y/n): ", end='')
        add_shadow = input().lower().startswith('y')
        
        remover.process_folder(folder_path, enhance=True, add_shadow=add_shadow)
    
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        if output_path:
            result = remover.remove_background(input_path, output_path)
        else:
            result = remover.process_image(input_path, enhance=True, add_shadow=False)
        
        if result:
            print(f"\n✅ İşlem başarıyla tamamlandı: {result}")
        else:
            print("\n❌ İşlem başarısız oldu.")


if __name__ == "__main__":
    main()
