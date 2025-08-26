#!/usr/bin/env python3
"""
Ultra Gelişmiş Kıyafet Arka Plan Kaldırıcı
En son AI modelleri ve akıllı optimizasyonlar ile
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from rembg import remove, new_session
import cv2
import time

class UltraClothingBgRemover:
    def __init__(self):
        # En son ve en gelişmiş modeller
        self.premium_models = {
            'isnet-general-use': {
                'description': 'DIS - En yeni nesil segmentasyon AI',
                'quality': 95,
                'speed': 80,
                'clothing_score': 90,
                'recommended': True
            },
            'sam': {
                'description': 'Meta SAM - Segment Anything Model',
                'quality': 98,
                'speed': 60,
                'clothing_score': 85,
                'recommended': True
            },
            'u2net_cloth_seg': {
                'description': 'Kıyafet özel eğitilmiş model',
                'quality': 85,
                'speed': 90,
                'clothing_score': 95,
                'recommended': True
            },
            'dis-general-use': {
                'description': 'DIS genel kullanım - yeni nesil',
                'quality': 92,
                'speed': 85,
                'clothing_score': 88,
                'recommended': True
            }
        }
        
        self.best_model = None
        self.session = None
        self.auto_select_best_model()
        
    def auto_select_best_model(self):
        """
        Sistemde mevcut olan en iyi modeli otomatik seç
        """
        print("🔍 En iyi model aranıyor...")
        
        # Öncelik sırası: kalite * kıyafet_skoru
        model_scores = {}
        
        for model_name, info in self.premium_models.items():
            if info['recommended']:
                score = (info['quality'] * info['clothing_score']) / 100
                model_scores[model_name] = score
        
        # En yüksek skordan başlayarak dene
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        
        for model_name, score in sorted_models:
            try:
                print(f"🧪 Test ediliyor: {model_name} (skor: {score:.1f})")
                self.session = new_session(model_name)
                self.best_model = model_name
                print(f"✅ Seçildi: {model_name}")
                print(f"📋 {self.premium_models[model_name]['description']}")
                return
            except Exception as e:
                print(f"❌ {model_name} yüklenemedi: {e}")
                continue
        
        # Hiçbiri çalışmazsa son çare
        print("⚠️  Premium modeller yüklenemedi, varsayılan kullanılıyor...")
        self.session = new_session('u2net')
        self.best_model = 'u2net'
    
    def intelligent_preprocessing(self, image_path):
        """
        Akıllı ön işleme - görüntü tipine göre optimize et
        """
        try:
            img = Image.open(image_path)
            original_size = img.size
            
            print(f"🧠 Akıllı analiz: {original_size[0]}x{original_size[1]}")
            
            # RGB'ye çevir
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Akıllı boyutlandırma
            max_dim = max(original_size)
            
            if max_dim < 512:
                # Küçük görüntü - büyüt
                scale_factor = 512 / max_dim
                new_size = (int(original_size[0] * scale_factor), 
                           int(original_size[1] * scale_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"📈 Büyütüldü: {original_size} -> {new_size}")
                
            elif max_dim > 2048:
                # Çok büyük görüntü - küçült
                scale_factor = 2048 / max_dim
                new_size = (int(original_size[0] * scale_factor), 
                           int(original_size[1] * scale_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"📉 Küçültüldü: {original_size} -> {new_size}")
            
            return img
            
        except Exception as e:
            print(f"❌ Ön işleme hatası: {e}")
            return Image.open(image_path)
    
    def ultra_background_removal(self, input_path, output_path=None):
        """
        Ultra gelişmiş arka plan kaldırma
        """
        try:
            print(f"\n🚀 ULTRA İŞLEM: {os.path.basename(input_path)}")
            print(f"🤖 Model: {self.best_model}")
            
            start_time = time.time()
            
            # Akıllı ön işleme
            processed_img = self.intelligent_preprocessing(input_path)
            
            # Byte array'e çevir
            import io
            img_byte_arr = io.BytesIO()
            processed_img.save(img_byte_arr, format='PNG', quality=95)
            input_data = img_byte_arr.getvalue()
            
            # Arka planı kaldır
            print("🧠 AI model çalışıyor...")
            output_data = remove(input_data, session=self.session)
            
            process_time = time.time() - start_time
            
            # Çıktı dosyası
            if output_path is None:
                input_file = Path(input_path)
                output_path = input_file.parent / f"{input_file.stem}_ultra_bg_removed.png"
            
            # Kaydet
            with open(output_path, 'wb') as f:
                f.write(output_data)
            
            print(f"✅ Tamamlandı: {process_time:.2f} saniye")
            print(f"📁 Çıktı: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Ultra işlem hatası: {e}")
            return None
    
    def ai_positioning(self, image_path, output_path=None, mode='smart'):
        """
        AI destekli akıllı konumlandırma
        """
        try:
            img = Image.open(image_path).convert("RGBA")
            width, height = img.size
            
            print(f"🧠 AI konumlandırma: {width}x{height}")
            
            # Alpha kanalından nesne analizi
            alpha = np.array(img)[:,:,3]
            non_zero_indices = np.where(alpha > 0)
            
            if len(non_zero_indices[0]) == 0:
                print("⚠️  Nesne bulunamadı")
                return image_path
            
            # Nesne sınırları
            top = np.min(non_zero_indices[0])
            bottom = np.max(non_zero_indices[0])
            left = np.min(non_zero_indices[1])
            right = np.max(non_zero_indices[1])
            
            object_height = bottom - top
            object_width = right - left
            
            # Optimal canvas boyutu
            base_size = max(object_width * 1.4, object_height * 1.3)
            canvas_width = canvas_height = int(base_size)
            
            # Minimum boyut garantisi
            canvas_width = max(canvas_width, 600)
            canvas_height = max(canvas_height, 600)
            
            # Yeni canvas oluştur
            new_canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
            
            # Konumlandır
            paste_x = (canvas_width - object_width) // 2
            if mode == 'smart':
                paste_y = int((canvas_height - object_height) * 0.25)  # Üstte
            else:
                paste_y = (canvas_height - object_height) // 2  # Merkez
            
            # Nesneyi kes ve yapıştır
            crop_box = (left, top, right + 1, bottom + 1)
            object_img = img.crop(crop_box)
            new_canvas.paste(object_img, (paste_x, paste_y), object_img)
            
            # Çıktı dosyası
            if output_path is None:
                input_file = Path(image_path)
                output_path = input_file.parent / f"{input_file.stem}_ai_positioned.png"
            
            new_canvas.save(output_path, "PNG")
            
            print(f"✅ AI konumlandırma: {canvas_width}x{canvas_height}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ AI konumlandırma hatası: {e}")
            return image_path
    
    def enhance_for_ecommerce(self, image_path, output_path=None):
        """E-ticaret iyileştirmesi"""
        try:
            img = Image.open(image_path).convert("RGBA")
            
            # RGB kısmını al
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            
            # İyileştirmeler
            enhancer = ImageEnhance.Contrast(rgb_img)
            rgb_img = enhancer.enhance(1.15)
            
            enhancer = ImageEnhance.Brightness(rgb_img)
            rgb_img = enhancer.enhance(1.05)
            
            enhancer = ImageEnhance.Sharpness(rgb_img)
            rgb_img = enhancer.enhance(1.1)
            
            # Alpha geri ekle
            final_img = rgb_img.convert("RGBA")
            final_img.putalpha(img.split()[3])
            
            if output_path is None:
                input_file = Path(image_path)
                output_path = input_file.parent / f"{input_file.stem}_ultra_enhanced.png"
            
            final_img.save(output_path, "PNG")
            print(f"✅ Ultra iyileştirme: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ İyileştirme hatası: {e}")
            return image_path
    
    def create_variants(self, image_path, output_dir=None):
        """Varyant oluşturma"""
        try:
            if output_dir is None:
                output_dir = Path(image_path).parent / "ultra_variants"
            else:
                output_dir = Path(output_dir)
            
            output_dir.mkdir(exist_ok=True)
            
            img = Image.open(image_path).convert("RGBA")
            base_name = Path(image_path).stem
            
            variants = {
                "thumbnail": (200, 200),
                "small": (400, 400),
                "medium": (800, 800),
                "large": (1200, 1200),
                "xl": (1600, 1600)
            }
            
            created_files = []
            
            for variant_name, size in variants.items():
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                
                canvas = Image.new("RGBA", size, (0, 0, 0, 0))
                paste_x = (size[0] - img_copy.width) // 2
                paste_y = (size[1] - img_copy.height) // 2
                canvas.paste(img_copy, (paste_x, paste_y), img_copy)
                
                variant_path = output_dir / f"{base_name}_ultra_{variant_name}.png"
                canvas.save(variant_path, "PNG")
                created_files.append(str(variant_path))
            
            return created_files
            
        except Exception as e:
            print(f"❌ Varyant hatası: {e}")
            return []
    
    def ultra_process(self, input_path, options=None):
        """
        Ultra tam işlem pipeline'ı
        """
        default_options = {
            'ai_positioning': True,
            'enhance': True,
            'create_variants': True,
            'positioning_mode': 'smart'
        }
        
        if options:
            default_options.update(options)
        
        print(f"\n{'='*60}")
        print(f"🚀 ULTRA PROCESS: {os.path.basename(input_path)}")
        print(f"{'='*60}")
        
        current_file = input_path
        
        # 1. Ultra arka plan kaldırma
        bg_removed = self.ultra_background_removal(current_file)
        if not bg_removed:
            return None
        current_file = bg_removed
        
        # 2. AI konumlandırma
        if default_options['ai_positioning']:
            positioned = self.ai_positioning(
                current_file,
                mode=default_options['positioning_mode']
            )
            current_file = positioned
        
        # 3. E-ticaret iyileştirmesi
        if default_options['enhance']:
            enhanced = self.enhance_for_ecommerce(current_file)
            current_file = enhanced
        
        # 4. Varyantlar
        if default_options['create_variants']:
            variants = self.create_variants(current_file)
            print(f"✅ {len(variants)} varyant oluşturuldu")
        
        print(f"\n🎉 ULTRA İŞLEM TAMAMLANDI!")
        print(f"📁 Son dosya: {current_file}")
        print(f"🤖 Kullanılan model: {self.best_model}")
        
        return current_file


def main():
    if len(sys.argv) < 2:
        print("""
🚀 ULTRA Kıyafet Arka Plan Kaldırıcı
En gelişmiş AI modelleri ile

Kullanım:
  python ultra_clothing_bg_remover.py <görüntü>
  python ultra_clothing_bg_remover.py --smart <görüntü>
  python ultra_clothing_bg_remover.py --center <görüntü>
        """)
        return
    
    remover = UltraClothingBgRemover()
    
    if sys.argv[1] == "--smart":
        if len(sys.argv) < 3:
            print("❌ Görüntü dosyası belirtiniz")
            return
        input_path = sys.argv[2]
        options = {'positioning_mode': 'smart'}
        
    elif sys.argv[1] == "--center":
        if len(sys.argv) < 3:
            print("❌ Görüntü dosyası belirtiniz")
            return
        input_path = sys.argv[2]
        options = {'positioning_mode': 'center'}
        
    else:
        input_path = sys.argv[1]
        options = {'positioning_mode': 'smart'}
    
    result = remover.ultra_process(input_path, options)
    
    if result:
        print(f"\n🎊 BAŞARILI!")
        print(f"📁 {os.path.basename(result)}")
    else:
        print(f"\n❌ İşlem başarısız")


if __name__ == "__main__":
    main()
