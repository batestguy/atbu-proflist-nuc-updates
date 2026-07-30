"""
Automated screenshot capture using PIL ImageGrab + ctypes (no pyautogui needed).
"""
import subprocess
import ctypes
import time
import os
import sys
from PIL import ImageGrab

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def click(x, y):
    """Click at screen coordinates using ctypes."""
    ctypes.windll.user32.SetCursorPos(x, y)
    time.sleep(0.1)
    ctypes.windll.mouse_event(0x0002, 0, 0, 0, 0)  # left down
    time.sleep(0.05)
    ctypes.windll.mouse_event(0x0004, 0, 0, 0, 0)  # left up
    time.sleep(0.3)

def capture(filename, delay=2):
    """Wait and take a full screenshot."""
    time.sleep(delay)
    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    img = ImageGrab.grab()
    img.save(filepath)
    kb = os.path.getsize(filepath) // 1024
    print(f"  OK: {filename} ({kb}KB)")

print("[SCREENSHOT] Automated Capture")
print("=" * 40)

# Kill any existing Python processes
os.system("taskkill /F /IM python.exe 2>nul")
time.sleep(1)

# Launch the app
print("[1] Launching app...")
app = subprocess.Popen(
    [r"D:\appdev-env\Scripts\python.exe", r"D:\Apps for ATBU\atbu_professors_app\main.py"],
    cwd=r"D:\Apps for ATBU\atbu_professors_app"
)
print("[2] Waiting for app to load (6 seconds)...")
time.sleep(6)

# Screenshot 1: Dashboard (default screen)
print("[3] Capturing Dashboard...")
capture("dashboard.png", delay=1)

# Screenshot 2: All Professors (click sidebar item 2)
print("[4] Capturing All Professors...")
click(160, 365)
capture("all_professors.png", delay=2)

# Screenshot 3: Add Professor
print("[5] Capturing Add Professor...")
click(160, 440)
capture("add_professor.png", delay=2)

# Screenshot 4: Import/Export
print("[6] Capturing Import/Export...")
click(160, 510)
capture("import_export.png", delay=2)

# Screenshot 5: About
print("[7] Capturing About...")
click(160, 590)
capture("about.png", delay=2)

# Screenshot 6: Settings
print("[8] Capturing Settings...")
click(160, 665)
capture("settings.png", delay=2)

# Close app
print("[9] Closing app...")
app.terminate()
try:
    app.wait(timeout=5)
except:
    app.kill()

print()
print("[DONE] All screenshots captured!")
print(f"  Folder: {SCREENSHOTS_DIR}")
for f in sorted(os.listdir(SCREENSHOTS_DIR)):
    if f.endswith('.png'):
        print(f"  - {f}")
