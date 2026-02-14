import pytest
import logging
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import time

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def driver():
    logger.info("=" * 70)
    logger.info("ИНИЦИАЛИЗАЦИЯ ВЕБДРАЙВЕРА")
    logger.info("=" * 70)
    
    chrome_options = Options()
    
    # === КРИТИЧЕСКИ ВАЖНЫЕ ОПЦИИ ДЛЯ БАНКА ===
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--user-data-dir=C:/jenkins-tests/chrome-profile")
    
    # === ОБХОД ДЕТЕКЦИИ АВТОМАТИЗАЦИИ ===
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # === ИНИЦИАЛИЗАЦИЯ ДРАЙВЕРА ===
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Скрипт обхода детекции
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    yield driver
    
    logger.info("Закрытие браузера...")
    driver.quit()
    logger.info("Браузер закрыт")

def attach_screenshot(driver, step_name):
    try:
        screenshot = driver.get_screenshot_as_png()
        allure.attach(screenshot, name=step_name, attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        logger.error(f"Ошибка прикрепления скриншота: {e}")

@allure.feature("Покупка товара")
@allure.story("Полный сценарий покупки")
def test_purchase_flow(driver):
    # === ШАГ 1: Открытие сайта ===
    with allure.step("Открытие сайта"):
        logger.info("Открытие сайта...")
        driver.get("https://demo1wp.shoporg.ru/")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        attach_screenshot(driver, "01_Главная_страница")
        logger.info("Сайт загружен")
    
    # === ШАГ 2: Закрытие всплывающих окон (если есть) ===
    with allure.step("Закрытие всплывающих окон"):
        time.sleep(2)
        try:
            # Попробуем найти и закрыть кнопку куков
            buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Принять') or contains(text(), 'Закрыть') or contains(text(), 'OK') or contains(text(), 'Согласен') or @aria-label='Close' or @class='popup-close']")
            for btn in buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        logger.info("Всплывающее окно закрыто")
                        time.sleep(1)
                        break
                except:
                    pass
        except Exception as e:
            logger.info(f"Всплывающие окна не найдены")
        attach_screenshot(driver, "02_После_закрытия_окон")
    
    # === ШАГ 3: Переход в каталог ===
    with allure.step("Переход в каталог"):
        logger.info("Поиск ссылки 'Каталог'...")
        
        # Вариант 1: точное совпадение
        try:
            catalog_link = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Каталог"))
            )
            catalog_link.click()
            logger.info("Ссылка 'Каталог' найдена по точному тексту")
        except:
            # Вариант 2: частичное совпадение
            try:
                catalog_link = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Каталог"))
                )
                catalog_link.click()
                logger.info("Ссылка 'Каталог' найдена по частичному тексту")
            except:
                # Вариант 3: поиск по классу меню
                try:
                    menu_items = driver.find_elements(By.CSS_SELECTOR, "a, .menu-item a, nav a")
                    logger.info(f"Найдено элементов меню: {len(menu_items)}")
                    
                    found = False
                    for item in menu_items:
                        try:
                            text = item.text.strip().lower()
                            if "каталог" in text or "catalog" in text or "products" in text:
                                WebDriverWait(driver, 15).until(EC.element_to_be_clickable(item)).click()
                                logger.info(f"Найден и кликнут элемент меню: {text}")
                                found = True
                                break
                        except:
                            pass
                    
                    if not found:
                        raise Exception("Ссылка 'Каталог' не найдена")
                except Exception as e:
                    logger.error(f"Не удалось найти меню: {e}")
                    attach_screenshot(driver, "03_Ошибка_поиска_меню")
                    raise
        
        WebDriverWait(driver, 20).until(EC.url_changes(driver.current_url))
        attach_screenshot(driver, "03_Каталог")
        logger.info(f"URL после перехода: {driver.current_url}")
    
    # === ШАГ 4: Выбор товара 'Бумага для принтера' ===
    with allure.step("Выбор товара 'Бумага для принтера'"):
        product = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Бумага для принтера"))
        )
        product.click()
        WebDriverWait(driver, 20).until(EC.url_contains("/product/"))
        attach_screenshot(driver, "04_Страница_товара")
        logger.info("Товар выбран")
    
    # === ШАГ 5: Добавление в корзину ===
    with allure.step("Добавление в корзину"):
        add_to_cart = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "add-to-cart"))
        )
        add_to_cart.click()
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".woocommerce-message"), "добавлен")
        )
        attach_screenshot(driver, "05_Товар_в_корзине")
        logger.info("Товар добавлен в корзину")
    
    # === ШАГ 6: Переход в корзину ===
    with allure.step("Переход в корзину"):
        cart_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Просмотр корзины"))
        )
        cart_link.click()
        WebDriverWait(driver, 20).until(EC.url_contains("/cart/"))
        attach_screenshot(driver, "06_Корзина")
        logger.info("Переход в корзину выполнен")
    
    # === ШАГ 7: Оформление заказа ===
    with allure.step("Оформление заказа"):
        checkout = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Оформить заказ"))
        )
        checkout.click()
        WebDriverWait(driver, 20).until(EC.url_contains("/checkout/"))
        attach_screenshot(driver, "07_Оформление_заказа")
        logger.info("Переход к оформлению заказа")
    
    # === ШАГ 8: Заполнение данных покупателя ===
    with allure.step("Заполнение данных покупателя"):
        fake = Faker('ru_RU')
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "billing_first_name"))
        )
        
        driver.find_element(By.ID, "billing_first_name").send_keys(fake.first_name())
        driver.find_element(By.ID, "billing_last_name").send_keys(fake.last_name())
        driver.find_element(By.ID, "billing_address_1").send_keys(fake.street_address())
        driver.find_element(By.ID, "billing_city").send_keys(fake.city())
        driver.find_element(By.ID, "billing_postcode").send_keys("123456")
        driver.find_element(By.ID, "billing_phone").send_keys(fake.phone_number())
        driver.find_element(By.ID, "billing_email").send_keys(fake.email())
        
        attach_screenshot(driver, "08_Данные_покупателя")
        logger.info("Данные покупателя заполнены")
    
    # === ШАГ 9: Подтверждение заказа ===
    with allure.step("Подтверждение заказа"):
        place_order = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "place_order"))
        )
        place_order.click()
        
        WebDriverWait(driver, 35).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".woocommerce-thankyou-order-received"), "заказ")
        )
        attach_screenshot(driver, "09_Заказ_успешно_оформлен")
        logger.info("Заказ успешно оформлен!")
    
    # === ШАГ 10: Проверка успешного завершения ===
    with allure.step("Проверка успешного завершения"):
        assert "заказ" in driver.page_source.lower(), "Страница подтверждения заказа не найдена"
        logger.info("✅ Тест пройден успешно!")
