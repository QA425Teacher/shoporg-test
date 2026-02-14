import pytest
import logging
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def driver():
    logger.info("=" * 70)
    logger.info("ЗАПУСК ХРОМА ДЛЯ ДИАГНОСТИКИ")
    logger.info("=" * 70)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--user-data-dir=C:/jenkins-tests/chrome-profile")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    yield driver
    
    driver.quit()

def save_screenshot(driver, name):
    try:
        screenshot_path = f"screenshots/{name}.png"
        os.makedirs("screenshots", exist_ok=True)
        driver.save_screenshot(screenshot_path)
        logger.info(f"Скриншот сохранён: {screenshot_path}")
        
        with open(screenshot_path, "rb") as f:
            allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        logger.error(f"Ошибка сохранения скриншота: {e}")

def test_debug_site_access(driver):
    logger.info("=== ШАГ 1: Открытие сайта ===")
    driver.get("https://demo1wp.shoporg.ru/")
    save_screenshot(driver, "step1_after_open")
    
    logger.info(f"URL: {driver.current_url}")
    logger.info(f"Title: {driver.title}")
    logger.info(f"Статус код (через JS): {driver.execute_script('return document.readyState')}")
    
    time.sleep(3)
    
    logger.info("=== ШАГ 2: Проверка содержимого страницы ===")
    page_source = driver.page_source[:1000]
    logger.info(f"Первые 1000 символов HTML:\n{page_source}")
    
    save_screenshot(driver, "step2_page_content")
    
    logger.info("=== ШАГ 3: Поиск всех ссылок на странице ===")
    links = driver.find_elements(By.TAG_NAME, "a")
    logger.info(f"Найдено ссылок: {len(links)}")
    
    for i, link in enumerate(links[:10]):
        try:
            text = link.text.strip()
            href = link.get_attribute("href")
            logger.info(f"  [{i}] Текст: '{text}' | href: {href}")
        except:
            pass
    
    save_screenshot(driver, "step3_all_links")
    
    logger.info("=== ШАГ 4: Поиск меню навигации ===")
    try:
        nav = driver.find_element(By.TAG_NAME, "nav")
        logger.info(f"Найден тег <nav>: {nav.get_attribute('outerHTML')[:500]}")
    except Exception as e:
        logger.error(f"Тег <nav> не найден: {e}")
    
    save_screenshot(driver, "step4_navigation")
    
    logger.info("=== ШАГ 5: Проверка консоли браузера ===")
    logs = driver.get_log("browser")
    if logs:
        logger.info(f"Ошибки в консоли браузера:")
        for log in logs[:5]:
            logger.info(f"  {log}")
    else:
        logger.info("Консоль браузера чистая")
    
    save_screenshot(driver, "step5_console_check")
    
    logger.info("=== ДИАГНОСТИКА ЗАВЕРШЕНА ===")
    logger.info("Проверьте скриншоты в папке 'screenshots'")
