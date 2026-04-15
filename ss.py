import time
import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def scrape_barbershops(query="barber shop in visakhapatnam", max_results=20):

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")

    # Wait for results panel
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@aria-label,"Results for")]')))
    time.sleep(3)

    # Scroll to load results
    scrollable_div = driver.find_element(By.XPATH, '//div[contains(@aria-label,"Results for")]')

    for _ in range(10):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)

    data = []

    shops = driver.find_elements(By.CLASS_NAME, "Nv2PK")[:max_results]

    for i in range(len(shops)):
        try:
            # Re-fetch elements (avoids stale errors)
            shops = driver.find_elements(By.CLASS_NAME, "Nv2PK")
            shop = shops[i]

            # Name
            try:
                name = shop.find_element(By.CLASS_NAME, "qBF1Pd").text
            except:
                name = ""

            # Click correct element
            link = shop.find_element(By.CSS_SELECTOR, "a.hfpxzc")
            driver.execute_script("arguments[0].click();", link)

            # Wait for details panel
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[@data-item-id="address"]')))
            time.sleep(2)

            # ✅ Address (CORRECT SOURCE)
            try:
                address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]').text
            except:
                address = ""

            # Phone
            try:
                phone = driver.find_element(By.XPATH, '//button[contains(@data-item-id,"phone")]').text
            except:
                phone = ""

            # Email (real extraction, else blank)
            try:
                page_text = driver.page_source
                emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", page_text)
                email = emails[0] if emails else ""
            except:
                email = ""

            data.append({
                "Name": name,
                "Address": address,
                "Contact": phone,
                "Email": email
            })

        except Exception as e:
            print(f"Skipping {i}: {e}")
            continue

    driver.quit()

    df = pd.DataFrame(data)
    df.to_csv("barbershop_data.csv", index=False)

    return df


# ▶️ RUN
df = scrape_barbershops()
print(df.head())