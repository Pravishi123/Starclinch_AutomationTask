"""Screenshot capture helper used on test failure."""
import os
import re

from config.config import SCREENSHOT_DIR


def capture(driver, test_name: str, timestamp: str) -> str:
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", test_name)
    file_path = os.path.join(SCREENSHOT_DIR, f"{safe_name}_{timestamp}.png")
    driver.save_screenshot(file_path)
    return file_path
