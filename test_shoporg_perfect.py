import pytest
import logging
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from faker import Faker
import time
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def driver():
    logger.info("=" * 70)
    logger.info("ИНИЦИАЛИЗАЦИЯ ВЕБДРАЙВЕРА ДЛЯ JENKINS (HEADLESS)")
    logger.info("=" * 70)
    
    chrome_options = Options()
    
    # === КРИТИЧЕСКИ ВАЖНО ДЛЯ JENKINS ===
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--user-data-dir=C:/jenkins-tests/chrome-profile")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--log-level=3")
    
    # === ОБХОД ДЕТЕКЦИИ АВТОМАТИЗАЦИИ ===
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # === ИНИЦИАЛИЗАЦИЯ ДРАЙВЕРА ===
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Скрипты обхода детекции
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']})")
    
    yield driver
    
    driver.quit()

def attach_screenshot(driver, step_name):
    try:
        screenshot = driver.get_screenshot_as_png()
        allure.attach(screenshot, name=step_name, attachment_type=allure.attachment_type.PNG)
        # Сохраняем скриншот в файл для отладки в Jenkins
        os.makedirs("screenshots", exist_ok=True)
        with open(f"screenshots/{step_name}.png", "wb") as f:
            f.write(screenshot)
    except Exception as e:
        logger.error(f"Ошибка прикрепления скриншота: {e}")

@allure.feature("Покупка товара")
@allure.story("Полный сценарий покупки")
def test_purchase_flow(driver):
    # === ШАГ 1: Открытие сайта ===
    with allure.step("Открытие сайта"):
        logger.info("Открытие сайта...")
        driver.get("https://demo1wp.shoporg.ru/")
        
        # Увеличенный таймаут для headless-режима
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        attach_screenshot(driver, "01_Главная_страница")
        logger.info(f"URL: {driver.current_url}")
        logger.info(f"Title: {driver.title}")
        
        # Диагностика: проверяем содержимое страницы
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        if "cloudflare" in page_text or "captcha" in page_text or "blocked" in page_text:
            logger.error("Сайт заблокирован Cloudflare или показывает CAPTCHA!")
            attach_screenshot(driver, "01_Ошибка_блокировка")
            raise Exception("Сайт недоступен из-за блокировки")
    
    # === ШАГ 2: Открытие каталога товаров (УЛУЧШЕННЫЙ ПОИСК) ===
    with allure.step("Открытие каталога товаров"):
        logger.info("Поиск кнопки каталога (гибкий поиск)...")
        
        catalog_button = None
        
        # Попытка 1: Класс cat-nav-trigger
        try:
            catalog_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'cat-nav-trigger')]"))
            )
            logger.info("Найдена кнопка по классу 'cat-nav-trigger'")
        except:
            pass
        
        # Попытка 2: Класс menu-toggle
        if catalog_button is None:
            try:
                catalog_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'menu-toggle')]"))
                )
                logger.info("Найдена кнопка по классу 'menu-toggle'")
            except:
                pass
        
        # Попытка 3: Иконка бургера (мобильное меню)
        if catalog_button is None:
            try:
                catalog_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'burger') or contains(@class, 'hamburger')]"))
                )
                logger.info("Найдена кнопка бургера (мобильное меню)")
            except:
                pass
        
        # Попытка 4: Прямой поиск по тексту
        if catalog_button is None:
            try:
                catalog_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Каталог') or contains(text(), 'Меню')]"))
                )
                logger.info("Найдена кнопка по тексту")
            except:
                pass
        
        if catalog_button is None:
            logger.error("Кнопка каталога не найдена ни одним из методов!")
            # Сохраняем полный скриншот и содержимое страницы для диагностики
            attach_screenshot(driver, "02_Ошибка_кнопки_каталога")
            # Сохраняем HTML страницы
            with open("screenshots/page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source[:10000])  # Первые 10К символов
            raise Exception("Кнопка каталога не найдена")
        
        catalog_button.click()
        time.sleep(3)  # Увеличенная пауза для загрузки меню в headless
        attach_screenshot(driver, "02_Каталог_открыт")
        logger.info("Каталог товаров открыт")
    
    # === ШАГ 3: Навигация по категориям ===
    with allure.step("Навигация: Одежда → Мужская одежда"):
        logger.info("Поиск меню 'Одежда'...")
        
        # Гибкий поиск меню "Одежда"
        clothes_menu = None
        
        # Попытка 1: По ID
        try:
            clothes_menu = WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((By.XPATH, "//li[@id='menu-item-927']"))
            )
            logger.info("Меню 'Одежда' найдено по ID")
        except:
            pass
        
        # Попытка 2: По тексту
        if clothes_menu is None:
            try:
                clothes_menu = WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Одежда') or contains(text(), 'Clothing')]"))
                )
                logger.info("Меню 'Одежда' найдено по тексту")
            except:
                pass
        
        if clothes_menu is None:
            logger.error("Меню 'Одежда' не найдено!")
            attach_screenshot(driver, "03_Ошибка_меню_одежда")
            raise Exception("Меню 'Одежда' не найдено")
        
        ActionChains(driver).move_to_element(clothes_menu).perform()
        time.sleep(2)
        attach_screenshot(driver, "03_Меню_Одежда")
        
        # Поиск "Мужская одежда"
        logger.info("Поиск 'Мужская одежда'...")
        mens_clothes = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Мужская') or contains(text(), 'Men')]"))
        )
        mens_clothes.click()
        WebDriverWait(driver, 35).until(EC.url_contains("/product-category/"))
        attach_screenshot(driver, "04_Мужская_одежда")
        logger.info("Переход в категорию 'Мужская одежда'")
    
    # === ШАГ 4: Применение фильтра по цене ===
    with allure.step("Применение фильтра по цене"):
        logger.info("Ожидание ползунков фильтра...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'ui-slider-handle')]"))
        )
        
        sliders = driver.find_elements(By.XPATH, "//span[contains(@class, 'ui-slider-handle')]")
        logger.info(f"Найдено ползунков: {len(sliders)}")
        
        if len(sliders) >= 2:
            right_slider = sliders[1]
            logger.info("Перетаскиваем правый ползунок...")
            ActionChains(driver).drag_and_drop_by_offset(right_slider, -150, 0).perform()
            time.sleep(2)
        else:
            logger.warning("Ползунки не найдены, пропускаем фильтрацию")
        
        attach_screenshot(driver, "05_Фильтр_применен")
    
    # === ШАГ 5-11: Остальные шаги (без изменений, но с увеличенными таймаутами) ===
    # ... [остальной код теста без изменений, но с таймаутами 30-40 секунд] ...
    
    # === ШАГ 5: Выбор товара ===
    with allure.step("Выбор товара"):
        logger.info("Поиск товара...")
        product = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, "//h2[contains(text(), 'Повседневная белая мужская футболка-поло') or contains(text(), 'Casual white men')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", product)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", product)
        WebDriverWait(driver, 35).until(EC.url_contains("/product/"))
        attach_screenshot(driver, "06_Страница_товара")
        logger.info("Товар выбран")
    
    # === ШАГ 6: Установка количества ===
    with allure.step("Установка количества"):
        quantity_input = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@name='quantity']"))
        )
        quantity_input.clear()
        quantity_input.send_keys("2")
        attach_screenshot(driver, "07_Количество_установлено")
    
    # === ШАГ 7: Добавление в корзину ===
    with allure.step("Добавление в корзину"):
        add_to_cart = WebDriverWait(driver, 35).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@name='add-to-cart']"))
        )
        driver.execute_script("arguments[0].click();", add_to_cart)
        time.sleep(4)  # Увеличенная пауза для обработки запроса
        attach_screenshot(driver, "08_Товар_добавлен")
    
    # === ШАГ 8: Заполнение данных покупателя ===
    with allure.step("Заполнение данных покупателя"):
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.ID, "billing_first_name"))
        )
        
        fake = Faker('ru_RU')
        fields = {
            "billing_first_name": fake.first_name(),
            "billing_last_name": fake.last_name(),
            "billing_address_1": fake.street_address(),
            "billing_city": fake.city(),
            "billing_postcode": "123456",
            "billing_phone": fake.phone_number(),
            "billing_email": fake.email()
        }
        
        for field_id, value in fields.items():
            field = WebDriverWait(driver, 25).until(
                EC.visibility_of_element_located((By.ID, field_id))
            )
            field.clear()
            field.send_keys(value)
        
        attach_screenshot(driver, "09_Данные_покупателя")
    
    # === ШАГ 9: Чекбокс согласия ===
    with allure.step("Чекбокс согласия"):
        try:
            checkbox = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and contains(@id, 'terms')]"))
            )
            driver.execute_script("arguments[0].click();", checkbox)
        except:
            logger.warning("Чекбокс не найден, пропускаем")
        time.sleep(1)
        attach_screenshot(driver, "10_Чекбокс_согласия")
    
    # === ШАГ 10: Подтверждение заказа ===
    with allure.step("Подтверждение заказа"):
        place_order = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.ID, "place_order"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", place_order)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", place_order)
        
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".woocommerce-thankyou-order-received"))
        )
        attach_screenshot(driver, "11_Заказ_успешно_оформлен")
        logger.info("✅ Заказ успешно оформлен!")
    
    # === ШАГ 11: Проверка ===
    with allure.step("Проверка успешного завершения"):
        success_el = driver.find_element(By.CSS_SELECTOR, ".woocommerce-thankyou-order-received")
        assert "заказ" in success_el.text.lower() or "order" in success_el.text.lower()
        logger.info("✅ Тест пройден успешно!")
