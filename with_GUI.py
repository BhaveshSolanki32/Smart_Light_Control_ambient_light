import tkinter as tk
from tkinter import ttk
import threading
import time
from test_screen_grab import *
# Global flags and parameters
running = False
sync_thread = None
brightness = 500      # percentage (0-100)
refresh_rate = 0.1    # seconds between updates
dom_color = 3
brightness_extra=100
def sync_loop():
    print("Starting color sync...")
    global brightness, refresh_rate, running, dom_color, brightness_extra
    last_color = (0, 0, 0)
    last_brightness = 0
    while running:
        try:
            # Grab dominant color from the central region
            dominant_color = get_average_dominant_colors(dom_color)
            print(f"Updated color: RGB({dominant_color})")
            print(f"Updated brightness: {brightness_extra}")
            # Scale the RGB values by the brightness factor (as a percentage)
            scaled_color = tuple(min(255, int(c * (brightness_extra / 100))) for c in dominant_color)
            
            if scaled_color != last_color:
                set_bulb_color(*scaled_color)
                last_color = scaled_color
            
            if brightness != last_brightness:
                set_bulb_brightness(brightness)
                last_brightness = brightness
        except Exception as e:
            print(f"Color error: {e}")

        time.sleep(refresh_rate)

def start_sync():
    """Starts the background thread for syncing color."""
    global running, sync_thread
    if not running:
        running = True
        sync_thread = threading.Thread(target=sync_loop, daemon=True)
        sync_thread.start()
        start_stop_button.config(text="Stop")

def stop_sync():
    """Stops the color syncing loop."""
    global running
    running = False
    start_stop_button.config(text="Start")

def toggle_sync():
    """Toggle the syncing loop on or off."""
    if running:
        stop_sync()
    else:
        start_sync()

def on_brightness_change(val):
    """Updates the brightness value when the slider is moved."""
    global brightness
    brightness = float(val)

def on_numOfDomColor_change(val):
    global dom_color
    dom_color = int(round(float(val)))

def on_refresh_rate_change(val):
    """Updates the refresh rate when the slider is moved."""
    global refresh_rate
    refresh_rate = float(val)

def on_brightness_extra_change(val):
    global brightness_extra
    brightness_extra = float(val)


def on_closing():
    """Handle the window closing event."""
    global running
    running = False  # Stop the syncing loop
    root.destroy()   # Close the Tkinter window

def Reset_variables():
    global brightness, refresh_rate, running, dom_color, brightness_extra
    brightness = 500      # percentage (0-100)
    refresh_rate = 0.1    # seconds between updates
    dom_color = 3
    brightness_extra=100
    brightness_slider.set(brightness)
    domColor_slider.set(dom_color)
    ext_bright_slider.set(brightness_extra)
    refresh_slider.set(refresh_rate)

# Set up the Tkinter GUI
root = tk.Tk()
root.title("Lighting Control")

# Brightness slider (0% to 100%)
brightness_label = ttk.Label(root, text="Brightness (%)")
brightness_label.pack(pady=5)

brightness_slider = ttk.Scale(root, from_=0, to=100, orient='horizontal',
                              command=on_brightness_change, length=170)
brightness_slider.set(50)
brightness_slider.pack(pady=5)

# num of dom colors slider (0% to 100%)
domColor_label = ttk.Label(root, text="Number of dom colors")
domColor_label.pack(pady=5)

domColor_slider = ttk.Scale(root, from_=1, to=10, orient='horizontal',
                              command=on_numOfDomColor_change, length=170)
domColor_slider.set(3)
domColor_slider.pack(pady=5)

# Brightness extra slider (0% to 100%)
ext_bright_label = ttk.Label(root, text="Extra Brightness")
ext_bright_label.pack(pady=5)

ext_bright_slider = ttk.Scale(root, from_=0, to=200, orient='horizontal',
                              command=on_brightness_extra_change, length=170)
ext_bright_slider.set(100)
ext_bright_slider.pack(pady=5)

# Refresh Rate slider (0.05 to 1.0 seconds)
refresh_label = ttk.Label(root, text="Refresh Rate (seconds)")
refresh_label.pack(pady=5)

refresh_slider = ttk.Scale(root, from_=0.0, to=1.0, orient='horizontal',
                           command=on_refresh_rate_change,length=170)
refresh_slider.set(0.1)
refresh_slider.pack(pady=5)

frame = tk.Frame(root)  # Create a container frame
frame.pack(pady=10)

reset_button = ttk.Button(frame, text="Reset", command=Reset_variables)
reset_button.pack(side="left",pady=10)

# Start/Stop button to toggle the syncing loop
start_stop_button = ttk.Button(frame, text="Start", command=toggle_sync)
start_stop_button.pack(side="left",pady=10)
# Bind closing event

root.protocol("WM_DELETE_WINDOW", on_closing)
root.geometry("280x330")
root.mainloop()

