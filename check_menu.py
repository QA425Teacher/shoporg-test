from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://demo1wp.shoporg.ru/")
time.sleep(3)

# Ищем ВСЕ ссылки
links = driver.find_elements(By.TAG_NAME, "a")
print(f"\n{'='*60}")
print(f"НАЙДЕНО ССЫЛОК: {len(links)}")
print(f"{'='*60}\n")

for i, link in enumerate(links[:20]):
    text = link.text.strip()
    href = link.get_attribute("href") or ""
    if text:
        print(f"[{i:2d}] {text:40s} | {href[:60]}")

driver.quit()
