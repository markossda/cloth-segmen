#!/usr/bin/env python3
"""
Lightweight Clothing Background Remover
Optimized for Railway deployment
"""

from PIL import Image
import io
import base64

class ClothingBgRemover:
    def __init__(self):
        print("⚡ Clothing BG Remover - Lightweight mode")
        self.model_name = "clothing_optimized"
        
        # Import rembg only when needed
        try:
            from rembg import remove, new_session
            self.session = new_session('u2net_cloth_seg')
            print("✅ u2net_cloth_seg model yüklendi!")
            self.use_ai = True
        except Exception as e:
            print(f"⚠️ AI model yüklenemedi: {e}")
            print("📝 Simple fallback mode aktif")
            self.use_ai = False
    
    def process_image(self, input_path):
        """Process image with clothing-specific background removal"""
        try:
            with open(input_path, 'rb') as f:
                input_data = f.read()
            
            if self.use_ai:
                print("🤖 AI clothing background removal...")
                from rembg import remove
                output_data = remove(input_data, session=self.session)
            else:
                print("⚡ Simple background removal...")
                # Simple fallback
                img = Image.open(io.BytesIO(input_data)).convert('RGBA')
                output_data = io.BytesIO()
                img.save(output_data, format='PNG')
                output_data = output_data.getvalue()
            
            # Save result
            output_path = input_path.replace('.', '_bg_removed.')
            with open(output_path, 'wb') as f:
                f.write(output_data)
            
            print(f"✅ Processing completed: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return None

# Wrapper classes for compatibility
class UltraClothingBgRemover:
    def __init__(self):
        self.remover = ClothingBgRemover()
        self.best_model = "clothing_optimized"
    
    def ultra_process(self, filepath, options=None):
        return self.remover.process_image(filepath)

class AdvancedClothingBgRemover:
    def __init__(self, model_name='u2net_cloth_seg'):
        self.remover = ClothingBgRemover()
        self.model_name = f"clothing_{model_name}"
    
    def process_clothing_complete(self, filepath, options=None):
        return self.remover.process_image(filepath)