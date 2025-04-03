import io
import time
import numpy as np
import tinytuya
from PIL import ImageGrab
from collections import Counter
from colorthief import ColorThief

device_id = "d7549dfe3c9e28db26racv"
local_key = "^kts+/$fu!Wpd_O`"

bulb = tinytuya.BulbDevice(
    dev_id=device_id,
    address='Auto',
    local_key=local_key,
    version=3.5
)
bulb.set_socketPersistent(True)

def get_average_dominant_colors(num_colors=1, clamp_range=(10, 255)):
    # Capture the central region of the screen
    full_screen = ImageGrab.grab()
    width, height = full_screen.size    
    left = width // 4
    top = height // 4
    right = width * 3 // 4
    bottom = height * 3 // 4
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom)).resize((60, 45))
    
    # Save the screenshot to an in-memory bytes buffer
    buf = io.BytesIO()
    screenshot.save(buf, format='PNG')
    buf.seek(0)
    
    # Use ColorThief to get a palette of dominant colors
    try:
        ct = ColorThief(buf)
        palette=None
        if num_colors>1:
            palette = ct.get_palette(color_count=num_colors, quality=5)
        else:
            palette = [ct.get_color(quality=1)]
    except Exception as e:
        print(f"Error getting dominant colors: {e}")
    if palette==None:
        return [(50, 50, 50)]
    
    # Average the palette colors (unweighted, as ColorThief doesn't provide frequencies)
    avg_r = sum(color[0] for color in palette) / len(palette)
    avg_g = sum(color[1] for color in palette) / len(palette)
    avg_b = sum(color[2] for color in palette) / len(palette)
    
    # Clamp the averaged colors within the specified range
    avg_r = np.clip(avg_r, clamp_range[0], clamp_range[1])
    avg_g = np.clip(avg_g, clamp_range[0], clamp_range[1])
    avg_b = np.clip(avg_b, clamp_range[0], clamp_range[1])
    
    return (int(avg_r), int(avg_g), int(avg_b))


# def get_average_dominant_colors(num_colors=5, clamp_range=(10,255)):

#     full_screen = ImageGrab.grab()
#     width, height = full_screen.size    
#     left = width // 4
#     top = height // 4
#     right = width * 3 // 4
#     bottom = height * 3 // 4
    
#     screenshot = ImageGrab.grab(bbox=(left, top, right, bottom)).resize((60, 45))
    
#     img_array = np.array(screenshot, dtype=np.float64) 
    
#     pixels = img_array.reshape(-1, 3)
#     pixels = (pixels // 32) * 32

#     pixel_tuples = [tuple(map(int, pixel)) for pixel in pixels]
    
#     color_counts = Counter(pixel_tuples)
    
#     top_colors = color_counts.most_common(num_colors)
    
#     if not top_colors:
#         return (0, 0, 0)
    
#     total_weight = sum(count for _, count in top_colors)
#     avg_r = sum(r * count for (r, g, b), count in top_colors) / total_weight
#     avg_g = sum(g * count for (r, g, b), count in top_colors) / total_weight
#     avg_b = sum(b * count for (r, g, b), count in top_colors) / total_weight
#     avg_r = np.clip(avg_r, *clamp_range)
#     avg_g = np.clip(avg_g, *clamp_range)    
#     avg_b = np.clip(avg_b, *clamp_range)
#     return (int(avg_r), int(avg_g), int(avg_b))

def set_bulb_color(r, g, b):
    try:
        
        if bulb.status().get('dps', {}).get('21') != 'colour':
            bulb.set_value('21', 'colour')
            time.sleep(0.1)
        
        bulb.set_colour(r, g, b, nowait=True) 
        print(f"Updated color: RGB({r},{g},{b}")
        return True
    
    except Exception as e:
        print(f"Color error: {e}")
        return False

def set_bulb_brightness(brightness):
    try:
        bulb.set_brightness_percentage(brightness, nowait=True)
        print(f"Updated brightness: {brightness}")
        return True
    except Exception as e:
        print(f"Error setting brightness: {e}")
        return False

def main():

    print("Starting enhanced color sync...")
    last_color = (0, 0, 0)
    
    try:
        while True:

            dominant_color = get_average_dominant_colors(3,(0,255))
            
            if dominant_color != last_color:
                if set_bulb_color(*dominant_color):
                    last_color = dominant_color
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping color sync...")
    finally:
        bulb.set_socketPersistent(False)

if __name__ == "__main__":
    main()
