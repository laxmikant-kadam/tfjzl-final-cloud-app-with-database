"""Capture the two screenshots required by the final project submission.

Start the development server first (``python manage.py runserver``), then run:

    python scripts/capture_screenshots.py

The script uses Selenium with headless Chrome and saves:

    screenshots/03-admin-site.png
    screenshots/07-final.png
"""
import base64
import os
import sys
import time
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from onlinecourse.models import Choice, Course, Submission  # noqa: E402

from selenium import webdriver  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.common.keys import Keys  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402

BASE_URL = "http://127.0.0.1:8000"
SCREENSHOTS = BASE_DIR / "screenshots"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@12345"
LEARNER_USERNAME = "john"
LEARNER_PASSWORD = "Learner@123"
COURSE_NAME = "Django Application Development"


def capture_full_page(driver, path):
    """Save a full-page PNG using Chrome's DevTools protocol."""
    metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
    content = metrics.get("cssContentSize") or metrics.get("contentSize")
    width = max(1200, int(content["width"]))
    height = min(6000, int(content["height"]) + 20)
    driver.set_window_size(width, 900)
    time.sleep(0.3)
    data = driver.execute_cdp_cmd(
        "Page.captureScreenshot",
        {
            "format": "png",
            "captureBeyondViewport": True,
            "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1},
        },
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(data["data"]))
    print(f"Saved {path} ({width}x{height})")


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--force-device-scale-factor=1")
    driver = webdriver.Chrome(options=options)
    # Always render the admin site with its default light theme.
    driver.execute_cdp_cmd(
        "Emulation.setEmulatedMedia",
        {"features": [{"name": "prefers-color-scheme", "value": "light"}]},
    )
    wait = WebDriverWait(driver, 15)

    try:
        # Start from a clean attempt history so the result is attempt #1.
        Submission.objects.filter(
            enrollment__user__username=LEARNER_USERNAME
        ).delete()
        # --- Screenshot 1: admin site (Authentication and Authorization + OnlineCourse)
        driver.get(f"{BASE_URL}/admin/")
        driver.find_element(By.ID, "id_username").send_keys(ADMIN_USERNAME)
        password = driver.find_element(By.ID, "id_password")
        password.send_keys(ADMIN_PASSWORD)
        password.send_keys(Keys.ENTER)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content h1")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.app-onlinecourse")))
        time.sleep(0.5)
        capture_full_page(driver, SCREENSHOTS / "03-admin-site.png")

        # --- Screenshot 2: successful mock exam attempt
        driver.get(f"{BASE_URL}/login/")
        driver.find_element(By.ID, "username").send_keys(LEARNER_USERNAME)
        driver.find_element(By.ID, "psw").send_keys(LEARNER_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))

        course = Course.objects.get(name=COURSE_NAME)
        driver.get(f"{BASE_URL}/course/{course.id}/")

        take_exam = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#examForm']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", take_exam)
        take_exam.click()
        wait.until(EC.visibility_of_element_located((By.ID, "examForm")))

        correct_ids = Choice.objects.filter(
            question__course=course, is_correct=True
        ).values_list("id", flat=True)
        for choice_id in correct_ids:
            checkbox = driver.find_element(By.ID, f"choice_{choice_id}")
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();",
                checkbox,
            )
            time.sleep(0.1)

        submit = driver.find_element(By.CSS_SELECTOR, "#questionform button[type=submit]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit)
        driver.execute_script("arguments[0].click();", submit)

        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Congratulations"))
        time.sleep(0.5)
        capture_full_page(driver, SCREENSHOTS / "07-final.png")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
