from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
from config import OUTPUT_DIR

def create_thumbnail(image_path, episode_number, output_path=None):
    """Create professional anime thumbnail"""
    
    # Open image
    img = Image.open(image_path)
    
    # Resize to 16:9 if needed
    target_ratio = 16/9
    current_ratio = img.width / img.height
    
    if abs(current_ratio - target_ratio) > 0.01:
        if current_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))
    
    # Resize to 1920x1080
    img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
    
    # Enhance image
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.3)
    
    # Create drawing context
    draw = ImageDraw.Draw(img)
    
    # Add EPISODE text (bottom-left)
    try:
        font_size = 120
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    episode_text = f"EPISODE {episode_number}"
    
    # Position
    x_pos = 80
    y_pos = 1080 - 150
    
    # Draw shadow
    for offset in range(8, 0, -1):
        draw.text((x_pos + offset, y_pos + offset), episode_text, font=font, fill=(0, 0, 0, 200))
    
    # Draw main text
    draw.text((x_pos, y_pos), episode_text, font=font, fill=(255, 215, 0))
    
    # Add HINDI ribbon (top-right)
    ribbon_width = 200
    ribbon_height = 60
    ribbon_x = 1920 - ribbon_width - 50
    ribbon_y = 50
    
    # Draw ribbon background
    ribbon = Image.new('RGBA', (ribbon_width, ribbon_height), (255, 255, 255, 255))
    ribbon_draw = ImageDraw.Draw(ribbon)
    
    try:
        ribbon_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        ribbon_font = ImageFont.load_default()
    
    # Center text in ribbon
    bbox = ribbon_draw.textbbox((0, 0), "HINDI", font=ribbon_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (ribbon_width - text_width) // 2
    text_y = (ribbon_height - text_height) // 2
    
    ribbon_draw.text((text_x, text_y), "HINDI", font=ribbon_font, fill=(0, 0, 0))
    
    # Rotate ribbon
    ribbon = ribbon.rotate(45, expand=True)
    
    # Paste ribbon on image
    img.paste(ribbon, (ribbon_x, ribbon_y), ribbon)
    
    # Save output
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, f"thumbnail_ep{episode_number}.jpg")
    
    img.save(output_path, quality=95)
    return output_path

def create_poster(thumbnail_path, anime_name, poster_format, output_path=None):
    """Create poster with anime info"""
    
    # Load thumbnail
    thumb = Image.open(thumbnail_path)
    
    # Create poster canvas
    poster_width = 1920
    poster_height = 1080 + 400  # Extra space for text
    poster = Image.new('RGB', (poster_width, poster_height), (20, 20, 30))
    
    # Paste thumbnail
    poster.paste(thumb, (0, 0))
    
    # Add text area
    draw = ImageDraw.Draw(poster)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Draw poster format text
    y_offset = 1100
    for line in poster_format.split('\n'):
        draw.text((50, y_offset), line, font=font, fill=(255, 255, 255))
        y_offset += 40
    
    # Save
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, f"poster_{anime_name}.jpg")
    
    poster.save(output_path, quality=95)
    return output_path