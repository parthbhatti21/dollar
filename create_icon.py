#!/usr/bin/env python3
"""
Create an icon for Dollar Assistant app.
Generates a PNG icon with a dollar sign ($) symbol.
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    import sys
    
    # Create a 1024x1024 image (high resolution for macOS)
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circular background with gradient effect
    # Outer circle (shadow effect)
    draw.ellipse([20, 20, size-20, size-20], fill=(30, 30, 30, 255))
    # Main circle
    draw.ellipse([40, 40, size-40, size-40], fill=(0, 122, 255, 255))  # iOS blue
    
    # Try to use a system font, fallback to default
    try:
        # Try macOS system font
        font_size = 600
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
    
    # Draw dollar sign
    text = "$"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1] - 50  # Slightly higher for better centering
    
    # Draw white dollar sign
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Save as PNG
    output_path = os.path.join(os.path.dirname(__file__), "app_icon.png")
    img.save(output_path, 'PNG')
    print(f"✅ Icon created: {output_path}")
    
except ImportError:
    print("PIL/Pillow not available. Installing...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "--quiet"])
    # Re-import and continue
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a 1024x1024 image (high resolution for macOS)
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circular background with gradient effect
    # Outer circle (shadow effect)
    draw.ellipse([20, 20, size-20, size-20], fill=(30, 30, 30, 255))
    # Main circle
    draw.ellipse([40, 40, size-40, size-40], fill=(0, 122, 255, 255))  # iOS blue
    
    # Try to use a system font, fallback to default
    try:
        # Try macOS system font
        font_size = 600
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
    
    # Draw dollar sign
    text = "$"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1] - 50  # Slightly higher for better centering
    
    # Draw white dollar sign
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Save as PNG
    output_path = os.path.join(os.path.dirname(__file__), "app_icon.png")
    img.save(output_path, 'PNG')
    print(f"✅ Icon created: {output_path}")

