#!/usr/bin/env python3
"""
Simple Background Remover - Render.com Compatible
Lightweight version without heavy dependencies
"""

from PIL import Image
import io

class SimpleBgRemover:
    def __init__(self):
        print("✅ Simple BG Remover initialized - lightweight mode")
        self.model_name = "simple_crop_remover"
    
    def process_image(self, input_path, options=None):
        """
        Simple background removal - center crop with transparency
        """
        print(f"🔄 Processing image: {input_path}")
        
        try:
            # Load image
            img = Image.open(input_path).convert('RGBA')
            width, height = img.size
            
            # Create transparent background
            result = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # Keep center portion (simple crop-based removal)
            margin_x = width // 6  # Keep 2/3 width
            margin_y = height // 8  # Keep 3/4 height
            
            # Copy center area
            for x in range(margin_x, width - margin_x):
                for y in range(margin_y, height - margin_y):
                    pixel = img.getpixel((x, y))
                    result.putpixel((x, y), pixel)
            
            # Save result
            output_path = input_path.replace('.', '_bg_removed.')
            result.save(output_path, 'PNG')
            
            print(f"✅ Simple processing completed: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Simple processing error: {e}")
            return None

class UltraClothingBgRemover:
    def __init__(self):
        print("⚡ Ultra BG Remover - Using simple fallback mode")
        self.simple_remover = SimpleBgRemover()
        self.best_model = "simple_ultra"
    
    def ultra_process(self, filepath, options=None):
        return self.simple_remover.process_image(filepath, options)

class AdvancedClothingBgRemover:
    def __init__(self, model_name='simple'):
        print(f"⚡ Advanced BG Remover - Using simple fallback mode: {model_name}")
        self.simple_remover = SimpleBgRemover()
        self.model_name = f"simple_{model_name}"
    
    def process_clothing_complete(self, filepath, options=None):
        return self.simple_remover.process_image(filepath, options)