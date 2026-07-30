"""Take a single screenshot. Usage: python snap1.py filename.png"""
import os, sys, time
from PIL import ImageGrab
sys.stdout.reconfigure(encoding='utf-8')

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(DIR, exist_ok=True)
time.sleep(3)

img = ImageGrab.grab()
name = sys.argv[1] if len(sys.argv) > 1 else "screenshot.png"
path = os.path.join(DIR, name)
img.save(path)
print(f"Saved: {path} ({os.path.getsize(path)//1024}KB)")
