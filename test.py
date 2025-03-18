import logging
from selenium.webdriver import Chrome, ChromeOptions, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import os

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(funcName)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('deepl_translator')

BASE_URL = "https://www.deepl.com/ru/translator"
MAX_RETRIES = 3
TIMEOUT = 15


def get_driver():
    """Настройка и возврат экземпляра Chrome"""
    logger.info("Первичная настройка...")
    options = ChromeOptions()
    options.add_argument("--lang=ru")
    options.add_argument("--headless=new")
    options.add_argument("--disable-infobars")
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1400,800")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    logger.info("Создание объекта браузера...")
    driver = Chrome(
        service=Service(executable_path="C:/chromedriver/chromedriver.exe"),
        options=options
    )
    driver.get(BASE_URL)
    accept_cookies(driver)
    set_russian_language(driver)
    return driver

def accept_cookies(driver):
    """Обработка куки-баннера"""
    try:
        cookie_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[3]/button[2]")))
        cookie_btn.click()
        logger.info("Куки приняты")
    except Exception as e:
        logger.warning(f"Куки-баннер не найден")


def set_russian_language(driver):
    """Явный выбор русского языка перевода"""
    try:
        logger.info("Установка исходного языка...")

        # XPath кнопки выбора целевого языка
        target_btn_xpath = ("/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/main/div[2]/nav/div/div[2]/"
                            "div/div/div[1]/div/div/div/div/div/section/div/div[1]/div[1]/div[1]"
                            "/div/div[1]/span/span/span/button")

        # Ожидаем и кликаем кнопку выбора языка
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, target_btn_xpath)))
        target_btn = driver.find_element(By.XPATH, target_btn_xpath)
        target_btn.click()

        # XPath кнопки английского языка из списка
        english_btn_xpath = ("/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/"
                             "main/div[2]/nav/div/div[2]/div/div/div[1]/div/div/div/div/div/"
                             "section/div/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div[2]/button[2]")

        # Выбираем английский язык
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, english_btn_xpath)))
        driver.find_element(By.XPATH, english_btn_xpath).click()

        logger.info("Исходный язык успешно установлен")

    except Exception as e:
        logger.error(f"Ошибка установки английского языка!")

    try:
        logger.info("Установка русского языка перевода...")

        # XPath кнопки выбора целевого языка
        target_btn_xpath = ("/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/main/div[2]/"
                            "nav/div/div[2]/div/div/div[1]/div/div/div/div/div/section/div/div[1]/div[1]/"
                            "div[3]/div[1]/div[1]/span/span/span/button")

        # Ожидаем и кликаем кнопку выбора языка
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, target_btn_xpath)))
        target_btn = driver.find_element(By.XPATH, target_btn_xpath)
        target_btn.click()

        # XPath кнопки русского языка из списка
        russian_btn_xpath = ("/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/main/div[2]/"
                             "nav/div/div[2]/div/div/div[1]/div/div/div/div/div/section/div/div[1]/div[1]/"
                             "div[3]/div[1]/div[1]/div/div/div[2]/div[2]/button[23]")

        # Выбираем русский язык
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, russian_btn_xpath)))
        driver.find_element(By.XPATH, russian_btn_xpath).click()

        logger.info("Язык перевода успешно установлен")

    except Exception as e:
        logger.error(f"Ошибка установки русского языка!")

def split_text(text, block_size=1500):
    """Разбивка текста на блоки"""
    return [text[i:i + block_size] for i in range(0, len(text), block_size)]


def translate_block(driver, text):
    """Основная функция перевода"""
    try:
        input_area = driver.find_element(By.CSS_SELECTOR, '[data-testid=translator-source-input]')

        # Очистка поля с триггером событий
        driver.execute_script("""
            arguments[0].value = '';
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
        """, input_area)

        # Вставка текста с имитацией ручного ввода
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
        """, input_area, text)

        # Имитация нажатия клавиши
        input_area.send_keys(" ")
        input_area.send_keys(Keys.BACK_SPACE)

        # Альтернативный вариант через JavaScript
        driver.execute_script("""
            const event = new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                bubbles: true,
                cancelable: true
            });
            arguments[0].dispatchEvent(event);
        """, input_area)

        # Ожидание перевода с проверкой каждые 0.5 секунд
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.find_element(By.CSS_SELECTOR, '[data-testid=translator-target-input]').text.strip() != ''
        )

        return driver.find_element(By.CSS_SELECTOR, '[data-testid=translator-target-input]').text

    except Exception as e:
        logger.error(f"Ошибка перевода: {str(e)}")
        raise


def main():
    driver = get_driver()
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            text = f.read()

        text_blocks = split_text(text)
        logger.info(f"Найдено блоков: {len(text_blocks)}")

        # driver.get(BASE_URL)
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-labelledby=translation-source-heading] d-textarea'))
        )

        with open("output.txt", "w", encoding="utf-8") as out_file:
            for i, block in enumerate(text_blocks):
                logger.info(f"Обработка блока {i + 1}/{len(text_blocks)}")
                translated = translate_block(driver, block)
                out_file.write(translated + "\n")
    except Exception as e:
        logger.error(f"Ошибка глобального уровня: {e}")

    finally:
        logger.info("Очистка пост процессов...")
        driver.quit()
        os.system("taskkill /f /IM chrome.exe >nul 2>&1")
        os.system("taskkill /f /IM chromedriver.exe >nul 2>&1")
        logger.info("Работа завершена корректно.")


if __name__ == "__main__":
    main()