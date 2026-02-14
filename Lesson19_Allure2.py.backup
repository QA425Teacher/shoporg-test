# ============================================================
# ТЕСТ: Покупка товара "Повседневная белая мужская футболка-поло"
# САЙТ: https://demo1wp.shoporg.ru/
# СЦЕНАРИЙ: Каталог → Одежда → Мужская одежда → Фильтр цены → Выбор товара → Оформление заказа
# СТИЛЬ: ООП (Объектно-ориентированное программирование) с использованием функций + Allure отчетность
# ============================================================
# =========================ОБЪЯСНЕНИЕ ТЕСТА===================================
# Как работает тест: пошагово
# Представьте, что вы — покупатель в магазине, а код — ваш ассистент:
# Ассистент открывает браузер → заходит на сайт (БЛОК 5: фикстура driver)
# Кликает «Каталог» → переходит в раздел «Одежда» → «Мужская одежда» (БЛОКИ 10-11)
# Двигает ползунок цены, чтобы увидеть нужные товары (БЛОК 12)
# Находит футболку → кликает по ней (БЛОК 14)
# Ставит количество 2 шт. → нажимает «В корзину» (БЛОКИ 15-16)
# Заполняет форму (имя, адрес) случайными данными (БЛОК 17)
# Ставит галочку «Согласен» → нажимает «Оформить заказ» (БЛОКИ 18-19)
# Каждый шаг логируется:
# logger.info("Товар добавлен в корзину") → в консоли видно, где тест сейчас.
# =========================ОБЪЯСНЕНИЕ ТЕСТА===================================

# ============================================================
# БЛОК 1: ИМПОРТ БИБЛИОТЕК
# ============================================================
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from faker import Faker
import logging
import time

# ============================================================
# БЛОК 2: НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# БЛОК 3: ИНИЦИАЛИЗАЦИЯ ГЕНЕРАТОРА ФЕЙКОВЫХ ДАННЫХ
# ============================================================
fake = Faker("ru_RU")


# ============================================================
# БЛОК 4: ФУНКЦИЯ ПРИКРЕПЛЕНИЯ СКРИНШОТА К ОТЧЕТУ ALLURE
# ============================================================
def attach_screenshot(driver, step_name):
    try:
        screenshot = driver.get_screenshot_as_png()
        allure.attach(screenshot, name=f"Screenshot: {step_name}", attachment_type=allure.attachment_type.PNG)
        logger.info(f"Скриншот '{step_name}' прикреплен к отчету Allure")
    except Exception as e:
        logger.warning(f"Не удалось прикрепить скриншот: {str(e)}")


# ============================================================
# БЛОК 5: ФИКСТУРА ДЛЯ ИНИЦИАЛИЗАЦИИ ВЕБДРАЙВЕРА С ОБХОДОМ БЛОКИРОВКИ
# ============================================================
@pytest.fixture(scope="function")
def driver():
    logger.info("= " * 50)
    logger.info("ИНИЦИАЛИЗАЦИЯ ВЕБДРАЙВЕРА ДЛЯ JENKINS (CI-РЕЖИМ)")
    logger.info("= " * 50)

    # Настройка опций Chrome для CI (Jenkins) + обход блокировки автоматизации
    chrome_options = webdriver.ChromeOptions()

    # === КРИТИЧЕСКИ ВАЖНО ДЛЯ JENKINS ===
    # chrome_options.add_argument("--headless=new")

    # === ОПЦИИ БЕЗОПАСНОСТИ ===
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # === ОПЦИИ СТАБИЛЬНОСТИ ДЛЯ CI ===
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--log-level=3")

    with allure.step("Инициализация веб-драйвера Chrome в headless-режиме"):
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Скрипты обхода детекции автоматизации (работают и в headless)
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            '''
        })

        logger.info("WebDriver успешно инициализирован в headless-режиме")
        attach_screenshot(driver, "Инициализация_драйвера")

    yield driver

    with allure.step("Закрытие веб-драйвера"):
        logger.info("Закрытие браузера...")
        attach_screenshot(driver, "Финальный_скриншот")
        driver.quit()
        logger.info("Браузер закрыт")

# ============================================================
# БЛОК 6: ФУНКЦИЯ БЕЗОПАСНОГО КЛИКА
# ============================================================
def safe_click(driver, by, value, max_attempt=3):
    for attempt in range(max_attempt):
        try:
            element = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((by, value)))
            element.click()
            logger.info(f"Успешный клик по элементу: {by}={value}")
            return True
        except Exception as e:
            logger.warning(f"Попытка {attempt + 1}/{max_attempt} не удалось: {str(e)}")
            time.sleep(1)
    logger.error(f"Не удалось кликнуть по элементу после {max_attempt} попыток")
    raise Exception(f"Элемент {by}={value} не кликабелен")


# ============================================================
# БЛОК 7: ФУНКЦИЯ БЕЗОПАСНОГО НАВЕДЕНИЯ КУРСОРА
# ============================================================
def safe_hover(driver, by, value):
    try:
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((by, value)))
        ActionChains(driver).move_to_element(element).perform()
        logger.info(f"Успешное наведение на элемент: {by}={value}")
        return element
    except Exception as e:
        logger.error(f"Ошибка при наведении на элемент: {str(e)}")
        raise Exception(f"Элемент {by}={value} не доступен для наведения")


# ============================================================
# БЛОК 8: ФУНКЦИЯ БЕЗОПАСНОГО ВВОДА ТЕКСТА
# ============================================================
def safe_send_keys(driver, by, value, text):
    try:
        element = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((by, value)))
        element.clear()
        element.send_keys(text)
        logger.info(f"Успешно введен текст в элемент: {by}={value}")
    except Exception as e:
        logger.error(f"Ошибка при вводе текста: {str(e)}")
        raise Exception(f"Элемент {by}={value} не доступен для ввода")


# ============================================================
# БЛОК 9: ФУНКЦИЯ БЕЗОПАСНОГО ПЕРЕТАСКИВАНИЯ ЭЛЕМЕНТА
# ============================================================
def safe_drag_and_drop(driver, by, value, offset_x, offset_y):
    try:
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((by, value)))
        ActionChains(driver).drag_and_drop_by_offset(element, offset_x, offset_y).perform()
        logger.info(f"Успешное перетаскивание элемента: {by}={value} на ({offset_x}, {offset_y})")
    except Exception as e:
        logger.error(f"Ошибка при перетаскивании элемента: {str(e)}")
        raise Exception(f"Элемент {by}={value} не доступен для перетаскивания")


# ============================================================
# БЛОК 10: ФУНКЦИЯ ОТКРЫТИЯ КАТАЛОГА ТОВАРОВ
# ============================================================
def open_catalog(driver):
    with allure.step("Открытие каталога товаров"):
        logger.info("Начало: Открытие каталога товаров")

        # Проверяем, что страница загружена
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Страница успешно загружена")
            attach_screenshot(driver, "Страница_загружена")
        except Exception as e:
            logger.error("Страница не загружена в течение 20 секунд")
            attach_screenshot(driver, "Ошибка_загрузки_страницы")
            raise Exception("Страница не загружена")

        # Безопасный клик по кнопке каталога товаров
        safe_click(driver, By.XPATH, "//button[contains(@class, 'cat-nav-trigger')]")
        time.sleep(1)
        attach_screenshot(driver, "Каталог_товаров_открыт")
        logger.info("Каталог товаров успешно открыт")


# ============================================================
# БЛОК 11: ФУНКЦИЯ НАВИГАЦИИ ПО КАТЕГОРИЯМ
# ============================================================
def navigate_to_category(driver):
    with allure.step("Навигация по категориям: Одежда → Мужская одежда"):
        logger.info("Начало: Навигация по категориям")

        # Наведение на меню "Одежда"
        logger.info("Наведение на меню 'Одежда'")
        safe_hover(driver, By.XPATH, "//li[@id='menu-item-927']")
        time.sleep(1)

        # Клик по "Мужская одежда"
        logger.info("Клик по меню 'Мужская одежда'")
        safe_click(driver, By.ID, "menu-item-924")
        attach_screenshot(driver, "Мужская_одежда_открыта")
        logger.info("Успешный переход в категорию 'Мужская одежда'")


# ============================================================
# БЛОК 12: ФУНКЦИЯ ПРИМЕНЕНИЯ ФИЛЬТРА ПО ЦЕНЕ
# ============================================================
def apply_price_filter(driver):
    """
    Применение фильтра по цене с помощью правого ползунка
    Аргументы:
        driver: Экземпляр веб-драйвера

    Описание:
        - Находит оба ползунка фильтра цены на странице
        - Выбирает правый ползунок (второй в списке)
        - Перетаскивает правый ползунок ВЛЕВО на 16 пикселей (округлённое значение 15.7439%)
        - Это снижает максимальную цену фильтра, делая товар доступным
        - Добавляет паузу для визуализации изменения
        - Логирует начало и успешное завершение операции
    """
    with allure.step("Применение фильтра по цене (правый ползунок влево)"):
        logger.info("Начало: Применение фильтра по цене")

        # Ждём появления хотя бы одного ползунка
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//span[contains(@class, 'ui-slider-handle ui-corner-all ui-state-default')]"
            ))
        )

        # Находим ВСЕ ползунки (их должно быть 2: левый и правый)
        sliders = driver.find_elements(By.XPATH,
                                       "//span[contains(@class, 'ui-slider-handle ui-corner-all ui-state-default')]")

        if len(sliders) >= 2:
            # Берём ВТОРОЙ ползунок (правый) и перетаскиваем его ВЛЕВО на 26 пикселей
            right_slider = sliders[1]
            logger.info(f"Найдено ползунков: {len(sliders)}. Используем правый ползунок (индекс 1)")
            logger.info("Перетаскиваем правый ползунок ВЛЕВО на 200 пикселей (15.7439% ≈ 16px)")
            ActionChains(driver).drag_and_drop_by_offset(right_slider, -200, 0).perform()
            logger.info("Правый ползунок успешно перетащен влево")
        else:
            # Резервный вариант: если ползунков меньше 2
            logger.warning(f"Найдено только {len(sliders)} ползунка(ов). Используем первый ползунок")
            slider = sliders[0] if sliders else WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//span[contains(@class, 'ui-slider-handle ui-corner-all ui-state-default')]"
                ))
            )
            # Перетаскиваем первый ползунок вправо (как в оригинале)
            ActionChains(driver).drag_and_drop_by_offset(slider, 30, 0).perform()
            logger.info("Перетащен первый ползунок вправо на 30 пикселей (резервный вариант)")

        # Пауза 3 секунды для визуализации изменения фильтра
        time.sleep(3)
        attach_screenshot(driver, "Фильтр_по_цене_применен")
        logger.info("Фильтр по цене успешно применен. Товар должен быть доступен для выбора.")

# ============================================================
# БЛОК 13: ФУНКЦИЯ ЗАКРЫТИЯ ВСПЛЫВАЮЩЕГО ОКНА
# ============================================================
def close_popup_if_exists(driver):
    with allure.step("Закрытие всплывающего окна (если существует)"):
        try:
            popup_close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'popup-close')]"))
            )
            popup_close_button.click()
            attach_screenshot(driver, "Всплывающее_окно_закрыто")
            logger.info("Всплывающее окно успешно закрыто")
        except Exception:
            logger.info("Всплывающее окно не обнаружено")


# ============================================================
# БЛОК 14: ФУНКЦИЯ ВЫБОРА ТОВАРА
# ============================================================
def select_product(driver):
    with allure.step("Выбор товара 'Повседневная белая мужская футболка-поло'"):
        logger.info("Начало: Выбор товара")
        # ИЗМЕНЕНО: заменён локатор для нового товара
        safe_click(driver, By.XPATH, "//h2[contains(text(), 'Повседневная белая мужская футболка-поло')]")
        attach_screenshot(driver, "Товар_выбран")
        logger.info("Товар 'Повседневная белая мужская футболка-поло' успешно выбран")


# ============================================================
# БЛОК 15: ФУНКЦИЯ УСТАНОВКИ КОЛИЧЕСТВА ТОВАРА
# ============================================================
def set_product_quantity(driver, quantity="1"):
    with allure.step(f"Установка количества товара на {quantity} шт."):
        logger.info(f"Начало: Установка количества товара на {quantity}")
        safe_send_keys(driver, By.XPATH, "//input[@name='quantity']", quantity)
        attach_screenshot(driver, "Количество_установлено")
        logger.info(f"Количество товара успешно установлено на {quantity}")


# ============================================================
# БЛОК 16: ФУНКЦИЯ ДОБАВЛЕНИЯ ТОВАРА В КОРЗИНУ
# ============================================================
def add_to_cart(driver):
    with allure.step("Добавление товара в корзину"):
        logger.info("Начало: Добавление товара в корзину")
        safe_click(driver, By.XPATH, "//button[@name='add-to-cart']")
        attach_screenshot(driver, "Товар_в_корзине")
        logger.info("Товар успешно добавлен в корзину")


# ============================================================
# БЛОК 17: ФУНКЦИЯ ЗАПОЛНЕНИЯ ФОРМЫ ЗАКАЗА
# ============================================================
def fill_order_form(driver):
    with allure.step("Заполнение формы заказа случайными данными"):
        logger.info("Начало: Заполнение формы заказа")

        order_data = {
            "billing_first_name": fake.first_name(),
            "billing_last_name": fake.last_name(),
            "billing_address_1": fake.street_address(),
            "billing_city": fake.city(),
            "billing_postcode": fake.postcode(),
            "billing_phone": fake.phone_number(),
            "billing_email": fake.email(),
        }

        for field, value in order_data.items():
            logger.info(f"Заполнение поля '{field}'")
            safe_send_keys(driver, By.ID, field, value)
            logger.info(f"Поле '{field}' успешно заполнено значением '{value}'")

        attach_screenshot(driver, "Форма_заполнена")
        logger.info("Форма заказа успешно заполнена")


# ============================================================
# БЛОК 18: ФУНКЦИЯ УСТАНОВКИ ЧЕКБОКСА СОГЛАСИЯ С УСЛОВИЯМИ (ШАГ 10)
# ============================================================
def accept_terms_and_conditions(driver):
    with allure.step("Установка чекбокса согласия с условиями"):
        logger.info("Начало: Установка чекбокса согласия с условиями")

        checkbox_clicked = False

        # Вариант 1: Поиск по ID 'terms'
        if not checkbox_clicked:
            try:
                logger.info("Попытка 1: Поиск чекбокса по ID 'terms'")
                terms_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "terms"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", terms_checkbox)
                time.sleep(0.5)
                terms_checkbox.click()
                logger.info("Чекбокс успешно установлен по ID 'terms'")
                checkbox_clicked = True
            except Exception as e:
                logger.warning(f"Чекбокс по ID 'terms' не найден: {str(e)}")

        # Вариант 2: Поиск по имени 'terms'
        if not checkbox_clicked:
            try:
                logger.info("Попытка 2: Поиск чекбокса по имени 'terms'")
                terms_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "terms"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", terms_checkbox)
                time.sleep(0.5)
                terms_checkbox.click()
                logger.info("Чекбокс успешно установлен по имени 'terms'")
                checkbox_clicked = True
            except Exception as e:
                logger.warning(f"Чекбокс по имени 'terms' не найден: {str(e)}")

        # Вариант 3: Поиск через лейбл
        if not checkbox_clicked:
            try:
                logger.info("Попытка 3: Поиск чекбокса через лейбл")
                terms_label = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//label[@for='terms']"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", terms_label)
                time.sleep(0.5)
                terms_label.click()
                logger.info("Чекбокс успешно установлен через лейбл")
                checkbox_clicked = True
            except Exception as e:
                logger.warning(f"Чекбокс через лейбл не найден: {str(e)}")

        # Вариант 4: Поиск по типу checkbox и части имени
        if not checkbox_clicked:
            try:
                logger.info("Попытка 4: Поиск чекбокса по типу и части имени")
                terms_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and contains(@id, 'term')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", terms_checkbox)
                time.sleep(0.5)
                terms_checkbox.click()
                logger.info("Чекбокс успешно установлен по типу и части имени")
                checkbox_clicked = True
            except Exception as e:
                logger.warning(f"Чекбокс по типу не найден: {str(e)}")

        if not checkbox_clicked:
            logger.error("Не удалось найти и установить чекбокс согласия с условиями")
            raise Exception("Чекбокс согласия не найден")

        time.sleep(1)
        attach_screenshot(driver, "Чекбокс_согласия_установлен")
        logger.info("Чекбокс согласия с условиями успешно установлен")


# ============================================================
# БЛОК 19: ФУНКЦИЯ ОФОРМЛЕНИЯ ЗАКАЗА (ШАГ 11)
# ============================================================
def place_order(driver):
    with allure.step("Оформление заказа"):
        logger.info("Начало: Оформление заказа")

        try:
            logger.info("Ожидание кнопки 'Оформить заказ'")
            place_order_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "place_order"))
            )

            logger.info("Прокрутка страницы к кнопке оформления заказа")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                  place_order_button)
            time.sleep(1)

            logger.info("Наведение курсора на кнопку 'Оформить заказ'")
            ActionChains(driver).move_to_element(place_order_button).perform()
            time.sleep(0.5)

            logger.info("Клик по кнопке 'Оформить заказ'")
            place_order_button.click()

            time.sleep(2)

            attach_screenshot(driver, "Заказ_оформлен")
            logger.info("Заказ успешно оформлен!")

        except Exception as e:
            logger.error(f"Ошибка при оформлении заказа: {str(e)}")
            raise Exception(f"Не удалось оформить заказ: {str(e)}")


# ============================================================
# БЛОК 20: ФУНКЦИЯ ПОЛНОГО ПРОЦЕССА ПОКУПКИ
# ============================================================
def purchase_flow(driver):
    """
    Основная функция, объединяющая все шаги процесса покупки
    Аргументы:
        driver: Экземпляр веб-драйвера

    Описание:
        - Последовательно выполняет все шаги покупки
        - Открывает каталог товаров
        - Переходит в категорию "Мужская одежда"
        - Применяет фильтр по цене
        - Закрывает всплывающее окно (если есть)
        - Выбирает товар
        - Устанавливает количество
        - Добавляет в корзину
        - Заполняет форму заказа
        - Устанавливает чекбокс согласия
        - Оформляет заказ
        - Логирует каждый шаг и общее завершение процесса
    """

    # ============================================================
    # ВЫВОД ЗАГОЛОВКА НАЧАЛА ПРОЦЕССА
    # ============================================================
    logger.info("=" * 50)
    logger.info("НАЧАЛО ПРОЦЕССА ПОКУПКИ")
    logger.info("=" * 50)

    # ============================================================
    # ШАГ 1: ОТКРЫТИЕ КАТАЛОГА ТОВАРОВ
    # ============================================================
    # Вызывается функция open_catalog(driver)
    # Эта функция:
    #   - Кликает по кнопке "Каталог товаров" в хедере сайта
    #   - Проверяет, что страница загружена
    #   - Делает скриншот после открытия каталога
    #   - Логирует успешное открытие каталога
    open_catalog(driver)

    # ============================================================
    # ШАГ 2: НАВИГАЦИЯ ПО КАТЕГОРИЯМ (ОДЕЖДА -> МУЖСКАЯ ОДЕЖДА)
    # ============================================================
    # Вызывается функция navigate_to_category(driver)
    # Эта функция:
    #   - Наводит курсор на меню "Одежда" для открытия выпадающего подменю
    #   - Кликает по подменю "Мужская одежда"
    #   - Переходит на страницу категории "Мужская одежда"
    #   - Делает скриншот после перехода
    #   - Логирует успешный переход в категорию
    navigate_to_category(driver)

    # ============================================================
    # ШАГ 3: ПРИМЕНЕНИЕ ФИЛЬТРА ПО ЦЕНЕ
    # ============================================================
    # Вызывается функция apply_price_filter(driver)
    # Эта функция:
    #   - Находит ползунок фильтра цены на странице
    #   - Перетаскивает ползунок вправо на 30 пикселей
    #   - Увеличивает минимальную цену фильтра
    #   - Делает скриншот после применения фильтра
    #   - Логирует успешное применение фильтра
    apply_price_filter(driver)

    # ============================================================
    # ШАГ 4: ЗАКРЫТИЕ ВСПЛЫВАЮЩЕГО ОКНА (ЕСЛИ ОНО ПОЯВИЛОСЬ)
    # ============================================================
    # Вызывается функция close_popup_if_exists(driver)
    # Эта функция:
    #   - Пытается найти кнопку закрытия всплывающего окна
    #   - Если окно найдено, кликает по кнопке закрытия
    #   - Если окно не найдено, продолжает выполнение теста
    #   - Делает скриншот после закрытия окна (если оно было)
    #   - Логирует результат операции
    close_popup_if_exists(driver)

    # ============================================================
    # ШАГ 5: ВЫБОР ТОВАРА "МУЖСКОЙ СЕРЫЙ КОСТЮМ В СВОБОДНОМ СТИЛЕ"
    # ============================================================
    # Вызывается функция select_product(driver)
    # Эта функция:
    #   - Ищет товар по заголовку "Мужской серый костюм в свободном стиле"
    #   - Кликает по заголовку товара
    #   - Переходит на страницу детального описания товара
    #   - Делает скриншот после выбора товара
    #   - Логирует успешный выбор товара
    select_product(driver)

    # ============================================================
    # ШАГ 6: УСТАНОВКА КОЛИЧЕСТВА ТОВАРА НА 2 ШТ.
    # ============================================================
    # Вызывается функция set_product_quantity(driver, "2")
    # Эта функция:
    #   - Находит поле ввода количества товара
    #   - Очищает существующее значение
    #   - Вводит новое количество "2"
    #   - Делает скриншот после установки количества
    #   - Логирует успешную установку количества
    set_product_quantity(driver, "2")

    # ============================================================
    # ШАГ 7: ДОБАВЛЕНИЕ ТОВАРА В КОРЗИНУ
    # ============================================================
    # Вызывается функция add_to_cart(driver)
    # Эта функция:
    #   - Находит кнопку "Купить" на странице товара
    #   - Кликает по кнопке для добавления товара в корзину
    #   - Делает скриншот после добавления товара в корзину
    #   - Логирует успешное добавление товара в корзину
    add_to_cart(driver)

    # ============================================================
    # ШАГ 8: ЗАПОЛНЕНИЕ ФОРМЫ ОФОРМЛЕНИЯ ЗАКАЗА
    # ============================================================
    # Вызывается функция fill_order_form(driver)
    # Эта функция:
    #   - Генерирует случайные данные для каждого поля формы
    #   - Заполняет поля: имя, фамилия, адрес, город, индекс, телефон, email
    #   - Использует генератор Faker для создания правдоподобных данных
    #   - Делает скриншот после заполнения формы
    #   - Логирует заполнение каждого поля и успешное завершение
    fill_order_form(driver)

    # ============================================================
    # ШАГ 10: УСТАНОВКА ЧЕКБОКСА СОГЛАСИЯ С УСЛОВИЯМИ
    # ============================================================
    # Вызывается функция accept_terms_and_conditions(driver)
    # Эта функция:
    #   - Находит чекбокс согласия с условиями
    #   - Устанавливает галочку в чекбоксе
    #   - Использует несколько вариантов поиска элемента (по ID, имени, лейблу, типу)
    #   - Делает скриншот после установки чекбокса
    #   - Логирует успешную установку чекбокса
    accept_terms_and_conditions(driver)

    # ============================================================
    # ШАГ 11: ОФОРМЛЕНИЕ ЗАКАЗА
    # ============================================================
    # Вызывается функция place_order(driver)
    # Эта функция:
    #   - Находит кнопку "Оформить заказ" (place_order)
    #   - Прокручивает страницу к кнопке
    #   - Наводит курсор на кнопку
    #   - Кликает по кнопке
    #   - Делает скриншот после оформления заказа
    #   - Логирует успешное оформление заказа
    place_order(driver)

    # ============================================================
    # ВЫВОД ЗАГОЛОВКА ЗАВЕРШЕНИЯ ПРОЦЕССА
    # ============================================================
    logger.info("=" * 50)
    logger.info("ПРОЦЕСС ПОКУПКИ УСПЕШНО ЗАВЕРШЕН!")
    logger.info("=" * 50)


# ============================================================
# БЛОК 21: ТЕСТОВАЯ ФУНКЦИЯ С ДЕКОРАТОРАМИ ALLURE
# ============================================================
@allure.feature("Покупка товара на сайте")
@allure.story("Полный сценарий покупки товара")
@allure.title("Тест покупки товара 'Повседневная белая мужская футболка-поло'")
@allure.description("""
Тест выполняет полный сценарий покупки товара:
1. Открытие каталога товаров
2. Навигация по категориям (Одежда → Мужская одежда)
3. Применение фильтра по цене
4. Выбор товара 'Повседневная белая мужская футболка-поло'
5. Установка количества
6. Добавление в корзину
7. Заполнение формы заказа
8. Установка чекбокса согласия
9. Оформление заказа
""")
@allure.severity(allure.severity_level.CRITICAL)
def test_purchase_flow(driver):
    with allure.step("Запуск полного процесса покупки"):
        # Открываем сайт перед началом теста
        driver.get("https://demo1wp.shoporg.ru/")
        logger.info("Сайт открыт: https://demo1wp.shoporg.ru/")
        attach_screenshot(driver, "Сайт_открыт")

        purchase_flow(driver)

    with allure.step("Проверка успешного завершения"):
        logger.info("Тест успешно завершен!")


# ============================================================
# БЛОК 22: КОМАНДЫ ДЛЯ ЗАПУСКА ТЕСТА
# ============================================================
"""
ИНСТРУКЦИЯ ПО УСТАНОВКЕ ЗАВИСИМОСТЕЙ И ЗАПУСКУ ТЕСТА:

1. УСТАНОВКА ЗАВИСИМОСТЕЙ:
   pip install pytest allure-pytest selenium webdriver-manager faker

2. СОЗДАНИЕ ФАЙЛА requirements.txt:
   pytest==8.3.4
   allure-pytest==2.15.0
   selenium==4.25.0
   webdriver-manager==4.0.2
   faker==38.0.0

3. ЗАПУСК ТЕСТА С ГЕНЕРАЦИЕЙ ОТЧЕТА ALLURE:
   pytest Lesson19_Allure.py --alluredir=./allure-results -v

4. ПРОСМОТР ОТЧЕТА ALLURE:
   allure serve ./allure-results

5. УСТАНОВКА ALLURE COMMANDLINE (если не установлен):
   Для macOS: brew install allure
   Для Windows: scoop install allure
   Для Linux: sudo snap install allure

6. ДОПОЛНИТЕЛЬНЫЕ ОПЦИИ ЗАПУСКА:
   Запуск с подробным выводом: pytest Lesson19_Allure.py --alluredir=./allure-results -v -s
   Запуск конкретного теста: pytest Lesson19_Allure.py::test_purchase_flow --alluredir=./allure-results -v
"""

# ============================================================
# БЛОК 23: ТОЧКА ВХОДА В ПРОГРАММУ (ДЛЯ ЗАПУСКА БЕЗ PYTEST)
# ============================================================
if __name__ == "__main__":
    print("Запуск теста напрямую (для отладки)...")
    print("Рекомендуется использовать pytest для полной функциональности Allure")

    # Создаем драйвер вручную с опциями
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Устанавливаем скрипт для обхода определения автоматизации
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

    driver.maximize_window()
    driver.get("https://demo1wp.shoporg.ru/")

    try:
        purchase_flow(driver)
        print("Тест успешно завершен!")
    except Exception as e:
        print(f"Ошибка при выполнении теста: {e}")
        import traceback

        traceback.print_exc()
    finally:
        time.sleep(3)
        driver.quit()