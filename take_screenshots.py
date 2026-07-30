"""
Capture screenshots of each screen for GitHub README.
Run this while the app is open - it takes screenshots at intervals.
"""
import pyautogui
import time
import os

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

print("📸 Screenshot Capture Tool")
print("=" * 40)
print("Instructions:")
print("1. The app will launch in 3 seconds")
print("2. Navigate to each screen")
print("3. Press ENTER to capture each screenshot")
print("4. Press 'q' + ENTER to quit")
print("=" * 40)
print()

screens = [
    ("dashboard.png", "Dashboard"),
    ("all_professors.png", "All Professors"),
    ("add_professor.png", "Add Professor"),
    ("import_export.png", "Import/Export"),
    ("about.png", "About"),
    ("settings.png", "Settings"),
]

for filename, screen_name in screens:
    input(f"📌 Navigate to '{screen_name}' and press ENTER to capture...")
    time.sleep(0.5)  # Small delay for UI to settle
    
    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    print(f"   ✅ Saved: {filename}")

print()
print("🎉 All screenshots captured!")
print(f"📁 Saved to: {SCREENSHOTS_DIR}")
