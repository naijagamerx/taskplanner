#!/usr/bin/env python3
"""
Create a simple application icon for Task Planner
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create application icon in multiple formats"""
    
    # Create icons directory
    icons_dir = "assets/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # Icon sizes for different platforms
    sizes = {
        'ico': [16, 32, 48, 64, 128, 256],  # Windows ICO
        'png': [512],  # High-res PNG
        'icns_sizes': [16, 32, 64, 128, 256, 512]  # macOS ICNS
    }
    
    # Colors
    bg_color = "#2B5CE6"  # Blue background
    text_color = "#FFFFFF"  # White text
    
    print("🎨 Creating Task Planner icons...")
    
    # Create PNG icons
    for size in sizes['png']:
        img = Image.new('RGBA', (size, size), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            font_size = size // 4
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Draw task icon (checkmark + list)
        # Draw checkmark
        check_size = size // 3
        check_x = size // 6
        check_y = size // 4
        
        # Checkmark lines
        draw.line([
            (check_x, check_y + check_size//2),
            (check_x + check_size//3, check_y + check_size*2//3),
            (check_x + check_size, check_y + check_size//4)
        ], fill=text_color, width=max(2, size//64))
        
        # Draw list lines
        list_x = check_x + check_size + size//8
        list_y = check_y
        line_height = check_size // 4
        
        for i in range(3):
            y = list_y + i * line_height
            draw.rectangle([
                list_x, y,
                list_x + check_size, y + line_height//3
            ], fill=text_color)
        
        # Save PNG
        png_path = os.path.join(icons_dir, f"app_icon_{size}.png")
        img.save(png_path, "PNG")
        print(f"   ✅ Created: {png_path}")
    
    # Create Windows ICO file
    try:
        ico_images = []
        for size in sizes['ico']:
            img = Image.new('RGBA', (size, size), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Scale the drawing for smaller sizes
            scale = size / 512
            
            # Draw checkmark
            check_size = int(size // 3)
            check_x = int(size // 6)
            check_y = int(size // 4)
            
            # Checkmark
            line_width = max(1, int(size // 64))
            draw.line([
                (check_x, check_y + check_size//2),
                (check_x + check_size//3, check_y + check_size*2//3),
                (check_x + check_size, check_y + check_size//4)
            ], fill=text_color, width=line_width)
            
            # List lines
            list_x = check_x + check_size + size//8
            list_y = check_y
            line_height = max(2, check_size // 4)
            
            for i in range(3):
                y = list_y + i * line_height
                draw.rectangle([
                    list_x, y,
                    list_x + check_size, y + max(1, line_height//3)
                ], fill=text_color)
            
            ico_images.append(img)
        
        # Save ICO file
        ico_path = os.path.join(icons_dir, "app_icon.ico")
        ico_images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        print(f"   ✅ Created: {ico_path}")
        
    except Exception as e:
        print(f"   ⚠️  Could not create ICO file: {e}")
    
    # Create a simple PNG for other uses
    main_png_path = os.path.join(icons_dir, "app_icon.png")
    if not os.path.exists(main_png_path):
        # Copy the 512px version
        large_png = os.path.join(icons_dir, "app_icon_512.png")
        if os.path.exists(large_png):
            img = Image.open(large_png)
            img.save(main_png_path)
            print(f"   ✅ Created: {main_png_path}")
    
    print("🎉 Icon creation completed!")
    print(f"📁 Icons saved in: {icons_dir}")
    
    return True

if __name__ == "__main__":
    try:
        create_app_icon()
    except ImportError:
        print("❌ PIL (Pillow) is required to create icons")
        print("Install it with: pip install Pillow")
    except Exception as e:
        print(f"❌ Error creating icons: {e}")
