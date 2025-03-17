import logging
from selenium.webdriver import Chrome, ChromeOptions
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
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-infobars")
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1400,800")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = Chrome(
        service=Service(executable_path="C:/chromedriver/chromedriver.exe"),
        options=options
    )
    return driver


def split_text(text, block_size=5000):
    """Разбивка текста на блоки"""
    return [text[i:i + block_size] for i in range(0, len(text), block_size)]


def translate_block(driver, text, retries=MAX_RETRIES):
    """Перевод одного блока текста"""
    for attempt in range(retries):
        try:
            # Очистка поля ввода
            driver.execute_script(
                "document.querySelector('[aria-labelledby=translation-source-heading] d-textarea').value = ''")

            # Вставка текста через JavaScript
            input_element = driver.find_element(By.CSS_SELECTOR,
                                                '[aria-labelledby=translation-source-heading] d-textarea')
            driver.execute_script("arguments[0].value = arguments[1];", input_element, text)

            # Ожидание перевода
            WebDriverWait(driver, TIMEOUT).until(
                lambda d: d.find_element(By.CSS_SELECTOR,
                                         '[aria-labelledby=translation-target-heading] d-textarea').text.strip() != ''
            )

            # Получение результата
            output_element = driver.find_element(By.CSS_SELECTOR,
                                                 '[aria-labelledby=translation-target-heading] d-textarea')
            return output_element.text
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            driver.refresh()
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[aria-labelledby=translation-source-heading] d-textarea'))
            )
    raise Exception("Max retries exceeded")


def main():
    driver = get_driver()
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            text = f.read()

        text_blocks = split_text(text)
        logger.info(f"Найдено блоков: {len(text_blocks)}")

        driver.get(BASE_URL)
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-labelledby=translation-source-heading] d-textarea'))
        )

        with open("output.txt", "w", encoding="utf-8") as out_file:
            for i, block in enumerate(text_blocks):
                logger.info(f"Обработка блока {i + 1}/{len(text_blocks)}")
                translated = translate_block(driver, block)
                out_file.write(translated + "\n")

    finally:
        driver.quit()
        os.system("taskkill /f /IM chrome.exe >nul 2>&1")
        os.system("taskkill /f /IM chromedriver.exe >nul 2>&1")


if __name__ == "__main__":
    main()