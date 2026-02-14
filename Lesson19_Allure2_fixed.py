import pytest
import logging
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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
    logger.info("ИНИЦИАЛИЗАЦИЯ ВЕБДРАЙВЕРА ДЛЯ БАНКОВСКОЙ СРЕДЫ")
    logger.info("=" * 70)
    
    chrome_options = webdriver.ChromeOptions()
    
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
    
    # === ИСПОЛЬЗУЕМ ВСТРОЕННЫЙ МЕНЕДЖЕР (без ручного пути) ===
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    
    logger.info(f"ChromeDriver: {service.path}")
    
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
    except:
        pass

@allure.feature("Покупка товара")
@allure.story("Полный сценарий покупки")
def test_purchase_flow(driver):
    with allure.step("Открытие сайта"):
        driver.get("https://demo1wp.shoporg.ru/")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        attach_screenshot(driver, "Главная_страница")
        logger.info("Сайт загружен")
    
    with allure.step("Переход в каталог"):
        catalog_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Каталог")))
        catalog_link.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/product-category/"))
        attach_screenshot(driver, "Каталог")
        logger.info("Переход в каталог выполнен")
    
    with allure.step("Выбор товара 'Бумага для принтера'"):
        product = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Бумага для принтера")))
        product.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/product/"))
        attach_screenshot(driver, "Страница_товара")
        logger.info("Товар выбран")
    
    with allure.step("Добавление в корзину"):
        add_to_cart = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "add-to-cart")))
        add_to_cart.click()
        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".woocommerce-message"), "добавлен"))
        attach_screenshot(driver, "Товар_в_корзине")
        logger.info("Товар добавлен в корзину")
    
    with allure.step("Переход в корзину"):
        cart_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Просмотр корзины")))
        cart_link.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/cart/"))
        attach_screenshot(driver, "Корзина")
        logger.info("Переход в корзину выполнен")
    
    with allure.step("Оформление заказа"):
        checkout = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Оформить заказ")))
        checkout.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/checkout/"))
        attach_screenshot(driver, "Оформление_заказа")
        logger.info("Переход к оформлению заказа")
    
    with allure.step("Заполнение данных покупателя"):
        fake = Faker('ru_RU')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "billing_first_name")))
        
        driver.find_element(By.ID, "billing_first_name").send_keys(fake.first_name())
        driver.find_element(By.ID, "billing_last_name").send_keys(fake.last_name())
        driver.find_element(By.ID, "billing_address_1").send_keys(fake.street_address())
        driver.find_element(By.ID, "billing_city").send_keys(fake.city())
        driver.find_element(By.ID, "billing_postcode").send_keys("123456")
        driver.find_element(By.ID, "billing_phone").send_keys(fake.phone_number())
        driver.find_element(By.ID, "billing_email").send_keys(fake.email())
        
        attach_screenshot(driver, "Данные_покупателя")
        logger.info("Данные покупателя заполнены")
    
    with allure.step("Подтверждение заказа"):
        place_order = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "place_order")))
        place_order.click()
        
        WebDriverWait(driver, 15).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".woocommerce-thankyou-order-received"), "заказ"))
        attach_screenshot(driver, "Заказ_успешно_оформлен")
        logger.info("Заказ успешно оформлен!")
    
    with allure.step("Проверка успешного завершения"):
        assert "заказ" in driver.page_source.lower(), "Страница подтверждения заказа не найдена"
        logger.info("✅ Тест пройден успешно!")
