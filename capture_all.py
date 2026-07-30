"""Navigate to each screen and capture screenshots."""
import ctypes
import time
import os
import sys
from PIL import ImageGrab
sys.stdout.reconfigure(encoding='utf-8')

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(DIR, exist_ok=True)

def click(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)
    time.sleep(0.2)
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(1.5)

def snap(name):
    img = ImageGrab.grab()
    path = os.path.join(DIR, name)
    img.save(path)
    print(f"OK: {name} ({os.path.getsize(path)//1024}KB)")

# Sidebar items (approximate Y positions based on screenshots)
# Dashboard=310, All Professors=370, Add Professor=440, Import/Export=510, About=590, Settings=660
sidebar_x = 160
items = [
    ("dashboard.png", 310),
    ("all_professors.png", 370),
    ("add_professor.png", 440),
    ("import_export.png", 510),
    ("about.png", 590),
    ("settings.png", 660),
]

for name, y in items:
    print(f"Clicking {name}...")
    click(sidebar_x, y)
    snap(name)
    time.sleep(0.5)

print("All screenshots captured!")
