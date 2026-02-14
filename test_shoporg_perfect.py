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

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def driver():
    logger.info("=" * 70)
    logger.info("ИНИЦИАЛИЗАЦИЯ ВЕБДРАЙВЕРА")
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
        logger.info(f"URL: {driver.current_url}")
        logger.info(f"Title: {driver.title}")
    
    # === ШАГ 2: Открытие каталога товаров ===
    with allure.step("Открытие каталога товаров"):
        logger.info("Клик по кнопке каталога товаров...")
        catalog_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'cat-nav-trigger')]"))
        )
        catalog_button.click()
        time.sleep(2)
        attach_screenshot(driver, "02_Каталог_открыт")
        logger.info("Каталог товаров открыт")
    
    # === ШАГ 3: Навигация по категориям (Одежда → Мужская одежда) ===
    with allure.step("Навигация: Одежда → Мужская одежда"):
        logger.info("Наведение на меню 'Одежда'...")
        clothes_menu = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//li[@id='menu-item-927']"))
        )
        ActionChains(driver).move_to_element(clothes_menu).perform()
        time.sleep(1)
        attach_screenshot(driver, "03_Меню_Одежда")
        
        logger.info("Клик по 'Мужская одежда'...")
        mens_clothes = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "menu-item-924"))
        )
        mens_clothes.click()
        WebDriverWait(driver, 25).until(EC.url_contains("/product-category/"))
        attach_screenshot(driver, "04_Мужская_одежда")
        logger.info("Переход в категорию 'Мужская одежда'")
    
    # === ШАГ 4: Применение фильтра по цене ===
    with allure.step("Применение фильтра по цене"):
        logger.info("Поиск ползунков фильтра цены...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'ui-slider-handle')]"))
        )
        
        sliders = driver.find_elements(By.XPATH, "//span[contains(@class, 'ui-slider-handle')]")
        logger.info(f"Найдено ползунков: {len(sliders)}")
        
        if len(sliders) >= 2:
            right_slider = sliders[1]
            logger.info("Перетаскиваем правый ползунок влево на 200 пикселей...")
            ActionChains(driver).drag_and_drop_by_offset(right_slider, -200, 0).perform()
            logger.info("Фильтр по цене применён")
        else:
            logger.warning("Найден только один ползунок")
            slider = sliders[0]
            ActionChains(driver).drag_and_drop_by_offset(slider, 30, 0).perform()
        
        time.sleep(3)
        attach_screenshot(driver, "05_Фильтр_применен")
    
    # === ШАГ 5: Выбор товара ===
    with allure.step("Выбор товара 'Повседневная белая мужская футболка-поло'"):
        logger.info("Поиск товара...")
        product = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//h2[contains(text(), 'Повседневная белая мужская футболка-поло')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", product)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", product)
        WebDriverWait(driver, 25).until(EC.url_contains("/product/"))
        attach_screenshot(driver, "06_Страница_товара")
        logger.info("Товар выбран")
    
    # === ШАГ 6: Установка количества товара ===
    with allure.step("Установка количества товара"):
        logger.info("Установка количества на 2 шт...")
        quantity_input = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@name='quantity']"))
        )
        quantity_input.clear()
        quantity_input.send_keys("2")
        attach_screenshot(driver, "07_Количество_установлено")
        logger.info("Количество установлено")
    
    # === ШАГ 7: Добавление в корзину ===
    with allure.step("Добавление в корзину"):
        logger.info("Добавление товара в корзину...")
        
        add_to_cart = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@name='add-to-cart']"))
        )
        driver.execute_script("arguments[0].click();", add_to_cart)
        
        # Ждём появления сообщения или перехода на страницу оформления
        time.sleep(3)
        
        attach_screenshot(driver, "08_Товар_добавлен")
        logger.info("Товар добавлен в корзину")
    
    # === ШАГ 8: Заполнение данных покупателя (МЫ УЖЕ НА СТРАНИЦЕ ОФОРМЛЕНИЯ) ===
    with allure.step("Заполнение данных покупателя"):
        logger.info("Заполнение формы заказа...")
        
        # Ждём появления формы оформления заказа
        WebDriverWait(driver, 30).until(
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
            try:
                field = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.ID, field_id))
                )
                field.clear()
                field.send_keys(value)
                logger.info(f"Поле '{field_id}' заполнено")
            except Exception as e:
                logger.warning(f"Не удалось заполнить поле '{field_id}': {e}")
        
        attach_screenshot(driver, "09_Данные_покупателя")
        logger.info("Данные покупателя заполнены")
    
    # === ШАГ 9: Установка чекбокса согласия ===
    with allure.step("Установка чекбокса согласия"):
        logger.info("Установка чекбокса согласия...")
        
        checkbox_clicked = False
        
        # Попытка 1: Поиск по классу 'terms'
        if not checkbox_clicked:
            try:
                terms_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and contains(@id, 'terms')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", terms_checkbox)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", terms_checkbox)
                logger.info("Чекбокс установлен через JavaScript")
                checkbox_clicked = True
            except:
                pass
        
        # Попытка 2: Поиск через лейбл
        if not checkbox_clicked:
            try:
                terms_label = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//label[contains(@for, 'terms')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", terms_label)
                time.sleep(0.5)
                terms_label.click()
                logger.info("Чекбокс установлен через лейбл")
                checkbox_clicked = True
            except:
                pass
        
        if not checkbox_clicked:
            logger.warning("Чекбокс согласия не найден, продолжаем без него")
        
        time.sleep(1)
        attach_screenshot(driver, "10_Чекбокс_согласия")
    
    # === ШАГ 10: Подтверждение заказа (С ОЖИДАНИЕМ ИСЧЕЗНОВЕНИЯ ОВЕРЛЕЯ) ===
    with allure.step("Подтверждение заказа"):
        logger.info("Оформление заказа...")
        
        # Ждём, пока кнопка станет кликабельной (исчезнет оверлей)
        place_order = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "place_order"))
        )
        
        # Прокручиваем к кнопке
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", place_order)
        time.sleep(1)
        
        # Кликаем через JavaScript (надёжнее)
        driver.execute_script("arguments[0].click();", place_order)
        
        # Ждём появления сообщения об успешном заказе
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".woocommerce-thankyou-order-received"))
        )
        
        attach_screenshot(driver, "11_Заказ_успешно_оформлен")
        logger.info("Заказ успешно оформлен!")
    
    # === ШАГ 11: Проверка успешного завершения ===
    with allure.step("Проверка успешного завершения"):
        success_text = driver.find_element(By.CSS_SELECTOR, ".woocommerce-thankyou-order-received").text
        logger.info(f"Текст подтверждения: {success_text}")
        
        assert "заказ" in success_text.lower() or "order" in success_text.lower(), "Страница подтверждения заказа не найдена"
        logger.info("✅ Тест пройден успешно!")
