from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

URL = "https://archive.toonworld4all.me/episode/tokyo-ghoul-1x3"

def get_iframe():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Codespaces paths
    chrome_options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print("[+] Opening page...")
        driver.get(URL)

        wait = WebDriverWait(driver, 30)

        # 🔹 Click "Watch Online"
        print("[+] Clicking Watch Online...")
        watch_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(text(),'Watch')] | //button[contains(text(),'Watch')]"
            ))
        )
        driver.execute_script("arguments[0].click();", watch_btn)

        # 🔹 Wait for iframe
        print("[+] Waiting for iframe...")
        iframe = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )

        iframe_src = iframe.get_attribute("src")

        print("\n✅ IFRAME FOUND")
        print(iframe_src)

    except Exception as e:
        print("❌ Error:", e)

    finally:
        driver.quit()


if __name__ == "__main__":
    get_iframe()
