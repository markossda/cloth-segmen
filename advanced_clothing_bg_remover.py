#!/usr/bin/env python3
"""
Gelişmiş Kıyafet Arka Plan Kaldırıcı
rembg optimizasyonları ve boyut düzeltmeleri ile
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from rembg import remove, new_session
import cv2

class AdvancedClothingBgRemover:
    def __init__(self, model_name='u2net_cloth_seg'):
        self.model_name = model_name
        self.session = new_session(model_name)
        print(f"✅ Model yüklendi: {model_name}")
        
    def analyze_image(self, image_path):
        """
        Görüntüyü analiz et ve öneriler sun
        """
        try:
            img = Image.open(image_path)
            width, height = img.size
            aspect_ratio = width / height
            
            print(f"📏 Görüntü boyutu: {width}x{height}")
            print(f"📐 En-boy oranı: {aspect_ratio:.2f}")
            
            # Optimal boyut önerileri
            if width < 512 or height < 512:
                print("⚠️  Düşük çözünürlük - daha iyi sonuç için en az 512px öneriliriz")
            
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                print("⚠️  Alışılmadık en-boy oranı - kırpılma olabilir")
                
            return {
                'width': width,
                'height': height,
                'aspect_ratio': aspect_ratio,
                'format': img.format,
                'mode': img.mode
            }
            
        except Exception as e:
            print(f"❌ Analiz hatası: {e}")
            return None
    
    def preprocess_image(self, image_path, target_size=None, maintain_aspect=True):
        """
        Görüntüyü rembg için optimize et
        """
        try:
            img = Image.open(image_path)
            original_size = img.size
            
            # RGB'ye çevir
            if img.mode != 'RGB':
                img = img.convert('RGB')
                print(f"🔄 {img.mode} -> RGB dönüştürüldü")
            
            # Boyut optimizasyonu
            if target_size:
                if maintain_aspect:
                    # En-boy oranını koru
                    img.thumbnail(target_size, Image.Resampling.LANCZOS)
                    print(f"📏 Boyut ayarlandı: {original_size} -> {img.size}")
                else:
                    # Boyutu zorla değiştir
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                    print(f"🔄 Boyut zorlandı: {original_size} -> {img.size}")
            
            # Kalite iyileştirmesi
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            return img
            
        except Exception as e:
            print(f"❌ Ön işleme hatası: {e}")
            return None
    
    def remove_background_advanced(self, input_path, output_path=None, preprocess=True):
        """
        Gelişmiş arka plan kaldırma
        """
        try:
            print(f"\n🔄 İşleniyor: {os.path.basename(input_path)}")
            
            # Görüntüyü analiz et
            analysis = self.analyze_image(input_path)
            if not analysis:
                return None
            
            # Ön işleme
            if preprocess:
                # Optimal boyut hesapla
                original_w, original_h = analysis['width'], analysis['height']
                
                # rembg için optimal boyutlar (832x832 veya katları)
                optimal_sizes = [512, 640, 832, 1024]
                target_size = min(optimal_sizes, key=lambda x: abs(x - max(original_w, original_h)))
                
                print(f"🎯 Hedef boyut: {target_size}x{target_size}")
                
                processed_img = self.preprocess_image(
                    input_path, 
                    target_size=(target_size, target_size), 
                    maintain_aspect=True
                )
                
                if not processed_img:
                    # Ön işleme başarısızsa orijinal dosyayı kullan
                    with open(input_path, 'rb') as f:
                        input_data = f.read()
                else:
                    # Ön işlenmiş görüntüyü byte'a çevir
                    import io
                    img_byte_arr = io.BytesIO()
                    processed_img.save(img_byte_arr, format='PNG')
                    input_data = img_byte_arr.getvalue()
            else:
                with open(input_path, 'rb') as f:
                    input_data = f.read()
            
            # Arka planı kaldır
            print("🤖 rembg işlemi başlıyor...")
            output_data = remove(input_data, session=self.session)
            
            # Çıktı dosyası yolu
            if output_path is None:
                input_file = Path(input_path)
                output_path = input_file.parent / f"{input_file.stem}_no_bg.png"
            
            # Kaydet
            with open(output_path, 'wb') as f:
                f.write(output_data)
            
            print(f"✅ Arka plan kaldırıldı: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Arka plan kaldırma hatası: {e}")
            return None
    
    def fix_positioning(self, image_path, output_path=None, center_vertically=True, add_padding=True):
        """
        Görüntü konumlandırmasını düzelt
        """
        try:
            img = Image.open(image_path).convert("RGBA")
            width, height = img.size
            
            print(f"🔧 Konumlandırma düzeltiliyor: {width}x{height}")
            
            # Alpha kanalından nesne sınırlarını bul
            alpha = np.array(img)[:,:,3]
            non_zero_indices = np.where(alpha > 0)
            
            if len(non_zero_indices[0]) == 0:
                print("⚠️  Şeffaf olmayan piksel bulunamadı")
                return image_path
            
            # Nesne sınırları
            top = np.min(non_zero_indices[0])
            bottom = np.max(non_zero_indices[0])
            left = np.min(non_zero_indices[1])
            right = np.max(non_zero_indices[1])
            
            object_height = bottom - top
            object_width = right - left
            
            print(f"📦 Nesne boyutları: {object_width}x{object_height}")
            print(f"📍 Nesne konumu: ({left}, {top}) - ({right}, {bottom})")
            
            # Yeni canvas boyutu hesapla
            if add_padding:
                padding_ratio = 0.1  # %10 padding
                new_width = int(object_width * (1 + 2 * padding_ratio))
                new_height = int(object_height * (1 + 2 * padding_ratio))
                
                # Minimum boyut garantisi
                new_width = max(new_width, 400)
                new_height = max(new_height, 400)
            else:
                new_width = object_width
                new_height = object_height
            
            # Kare yapmak istersek
            canvas_size = max(new_width, new_height)
            new_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            
            # Nesneyi merkeze yerleştir
            if center_vertically:
                # Dikey merkez
                paste_y = (canvas_size - object_height) // 2
                # Yatay merkez  
                paste_x = (canvas_size - object_width) // 2
            else:
                # Üstten %20 boşluk bırak
                paste_y = int(canvas_size * 0.2)
                paste_x = (canvas_size - object_width) // 2
            
            # Nesneyi yeni konuma yapıştır
            crop_box = (left, top, right + 1, bottom + 1)
            object_img = img.crop(crop_box)
            new_canvas.paste(object_img, (paste_x, paste_y), object_img)
            
            # Çıktı dosyası
            if output_path is None:
                input_file = Path(image_path)
                output_path = input_file.parent / f"{input_file.stem}_positioned.png"
            
            new_canvas.save(output_path, "PNG")
            print(f"✅ Konumlandırma düzeltildi: {output_path}")
            print(f"📏 Yeni boyut: {canvas_size}x{canvas_size}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Konumlandırma hatası: {e}")
            return image_path
    
    def enhance_for_ecommerce(self, image_path, output_path=None):
        """
        E-ticaret için görüntüyü iyileştir
        """
        try:
            img = Image.open(image_path).convert("RGBA")
            
            # Kontrast iyileştirmesi (sadece RGB kanalları)
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])  # Alpha maskesi ile
            
            # Kontrast
            enhancer = ImageEnhance.Contrast(rgb_img)
            rgb_img = enhancer.enhance(1.15)
            
            # Parlaklık
            enhancer = ImageEnhance.Brightness(rgb_img)
            rgb_img = enhancer.enhance(1.05)
            
            # Keskinlik
            enhancer = ImageEnhance.Sharpness(rgb_img)
            rgb_img = enhancer.enhance(1.1)
            
            # Renk doygunluğu
            enhancer = ImageEnhance.Color(rgb_img)
            rgb_img = enhancer.enhance(1.1)
            
            # Alpha kanalını geri ekle
            final_img = rgb_img.convert("RGBA")
            final_img.putalpha(img.split()[3])  # Orijinal alpha kanalı
            
            # Çıktı dosyası
            if output_path is None:
                input_file = Path(image_path)
                output_path = input_file.parent / f"{input_file.stem}_enhanced.png"
            
            final_img.save(output_path, "PNG")
            print(f"✅ E-ticaret iyileştirmesi: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ İyileştirme hatası: {e}")
            return image_path
    
    def create_product_variants(self, image_path, output_dir=None):
        """
        Farklı boyutlarda ürün varyantları oluştur
        """
        try:
            if output_dir is None:
                output_dir = Path(image_path).parent / "variants"
            else:
                output_dir = Path(output_dir)
                
            output_dir.mkdir(exist_ok=True)
            
            img = Image.open(image_path).convert("RGBA")
            base_name = Path(image_path).stem
            
            # E-ticaret standart boyutları
            variants = {
                "thumbnail": (150, 150),
                "small": (300, 300),
                "medium": (600, 600),
                "large": (1200, 1200),
                "square": (800, 800)
            }
            
            created_files = []
            
            for variant_name, size in variants.items():
                # Boyutu ayarla (en-boy oranını koru)
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Kare canvas oluştur
                canvas = Image.new("RGBA", size, (0, 0, 0, 0))
                
                # Merkezle
                paste_x = (size[0] - img_copy.width) // 2
                paste_y = (size[1] - img_copy.height) // 2
                canvas.paste(img_copy, (paste_x, paste_y), img_copy)
                
                # Kaydet
                variant_path = output_dir / f"{base_name}_{variant_name}.png"
                canvas.save(variant_path, "PNG")
                created_files.append(str(variant_path))
                print(f"✅ Varyant oluşturuldu: {variant_name} ({size[0]}x{size[1]})")
            
            return created_files
            
        except Exception as e:
            print(f"❌ Varyant oluşturma hatası: {e}")
            return []
    
    def process_clothing_complete(self, input_path, options=None):
        """
        Tam kıyafet işleme pipeline'ı
        """
        default_options = {
            'preprocess': True,
            'fix_positioning': True,
            'center_vertically': False,  # Üstten boşluk bırak
            'enhance': True,
            'create_variants': False,
            'add_padding': True
        }
        
        if options:
            default_options.update(options)
        
        print(f"\n{'='*60}")
        print(f"🚀 TAM İŞLEM BAŞLIYOR: {os.path.basename(input_path)}")
        print(f"{'='*60}")
        
        current_file = input_path
        
        # 1. Arka planı kaldır
        bg_removed = self.remove_background_advanced(
            current_file, 
            preprocess=default_options['preprocess']
        )
        
        if not bg_removed:
            return None
            
        current_file = bg_removed
        
        # 2. Konumlandırmayı düzelt
        if default_options['fix_positioning']:
            positioned = self.fix_positioning(
                current_file,
                center_vertically=default_options['center_vertically'],
                add_padding=default_options['add_padding']
            )
            current_file = positioned
        
        # 3. E-ticaret iyileştirmesi
        if default_options['enhance']:
            enhanced = self.enhance_for_ecommerce(current_file)
            current_file = enhanced
        
        # 4. Varyantlar oluştur
        if default_options['create_variants']:
            variants = self.create_product_variants(current_file)
            print(f"✅ {len(variants)} varyant oluşturuldu")
        
        print(f"\n🎉 İşlem tamamlandı: {current_file}")
        return current_file


def main():
    if len(sys.argv) < 2:
        print("""
🔧 Gelişmiş Kıyafet Arka Plan Kaldırıcı

Kullanım:
  python advanced_clothing_bg_remover.py <görüntü_dosyası>
  python advanced_clothing_bg_remover.py --folder <klasör>
  python advanced_clothing_bg_remover.py --analyze <görüntü>
  
Örnekler:
  python advanced_clothing_bg_remover.py tshirt.jpg
  python advanced_clothing_bg_remover.py --folder ./products
  python advanced_clothing_bg_remover.py --analyze product.jpg
  
Özellikler:
  ✅ Otomatik boyut optimizasyonu
  ✅ Konumlandırma düzeltmesi
  ✅ E-ticaret iyileştirmesi
  ✅ Çoklu varyant oluşturma
        """)
        return
    
    remover = AdvancedClothingBgRemover()
    
    if sys.argv[1] == "--analyze":
        if len(sys.argv) < 3:
            print("❌ Analiz edilecek dosya belirtiniz")
            return
        analysis = remover.analyze_image(sys.argv[2])
        
    elif sys.argv[1] == "--folder":
        if len(sys.argv) < 3:
            print("❌ Klasör yolu belirtiniz")
            return
        
        folder = Path(sys.argv[2])
        if not folder.exists():
            print(f"❌ Klasör bulunamadı: {folder}")
            return
        
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        image_files = [f for f in folder.iterdir() 
                      if f.is_file() and f.suffix.lower() in supported_formats]
        
        print(f"📁 {len(image_files)} görüntü dosyası bulundu")
        
        for img_file in image_files:
            result = remover.process_clothing_complete(str(img_file))
        
    else:
        # Tek dosya işle
        input_path = sys.argv[1]
        
        # İşlem seçenekleri
        options = {
            'preprocess': True,
            'fix_positioning': True,
            'center_vertically': False,  # Tişört için üstten boşluk
            'enhance': True,
            'create_variants': True,  # Varyantlar oluştur
            'add_padding': True
        }
        
        result = remover.process_clothing_complete(input_path, options)
        
        if result:
            print(f"\n✅ BAŞARILI: {result}")
        else:
            print(f"\n❌ İşlem başarısız")


if __name__ == "__main__":
    main()
