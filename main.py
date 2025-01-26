import datetime
from time import sleep
from bs4 import BeautifulSoup
import requests
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
import random
from fake_useragent import FakeUserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import logging
import os


log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(funcName)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.DEBUG)


app_log = logging.getLogger('duo_logger')
app_log.setLevel(logging.DEBUG)
app_log.addHandler(stream_handler)


BASE_URL = "https://www.deepl.com/ru/translator"


def click_button(xpath: str, timeout=3) -> None:
    """
    Функция для нажатия на кнопку
    :param timeout: время ожидания
    :param xpath: путь к кнопке
    :return: None
    """
    cur_button = WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    cur_button.click()


def set_viewport_size(driver, width, height):
    window_size = driver.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
    driver.set_window_size(*window_size)


def random_mouse_movements(driver):
    app_log.info("Передвигаю курсор на рандомные точки...")
    for _ in range(30):
        try:
            x = random.randint(1 * _, 10 * _)
            y = random.randint(2 * _, 11 * _)
            ActionChains(driver) \
                .move_by_offset(x, y) \
                .perform()
        except Exception:
            continue


if __name__ == '__main__':
    app_log.info("Настройка браузера...")
    user_agent = FakeUserAgent().chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    # options.add_argument("--headless=new")
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument("--incognito")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(service=Service(executable_path="C:/chromedriver/chromedriver.exe"),
                               options=options)

    with open("input.txt", encoding="utf8") as file:
        app_log.info("Читаю текст из input файла")
        input_text = file.read()

    set_viewport_size(browser, 1400, 800)

    app_log.info("Открываю страницу Deepl...")
    browser.get(BASE_URL)
    # random_mouse_movements(browser)
    # Настроить язык.

    # Поиск входного поля, вставка значений
    input_label = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.XPATH,
                                                                                  '/html/body/div[1]/div[1]/div/div[3]'
                                                                                  '/div[2]/div[1]/div[2]/div[1]/main/'
                                                                                  'div[2]/nav/div/div[2]/div/div/'
                                                                                  'div[1]/div/div/div/section/div/'
                                                                                  'div[2]/div[1]/section/div/'
                                                                                  'div[1]/d-textarea/div[1]')))
    input_label.send_keys(input_text)
    input_label.send_keys(Keys.ENTER)

    app_log.info("Ожидаю перевод 5 секунд...")
    sleep(5)

    # Чтение выходных данных
    try:
        result_field = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.XPATH,
                                                                                      '/html/body/div[1]/div[1]/div/div[3]'
                                                                                      '/div[2]/div[1]/div[2]/div[1]/main/'
                                                                                      'div[2]/nav/div/div[2]/div/div/'
                                                                                      'div[1]/div/div/div/section/div/'
                                                                                      'div[2]/div[3]/section/div[1]/'
                                                                                      'd-textarea/div')))
    except Exception:
        result_field = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.XPATH,
                                                                                       '/html/body/div[1]/div[1]/div/'
                                                                                       'div[2]/div[2]/div[1]/div[2]/'
                                                                                       'div[1]/main/div[2]/nav/div/'
                                                                                       'div[2]/div/div/div[1]/div/div/'
                                                                                       'div/section/div/div[2]/div[3]/'
                                                                                       'section/div[1]/d-textarea/'
                                                                                       'div')))
    result_text = result_field.text
    app_log.info("Вывод данных в файл...")
    print(result_text)

    browser.close()
    app_log.info("Закрываю браузер. Завершение работы программы.")
    os.system("taskkill /f /IM chrome.exe >nul 2>&1")
    os.system("taskkill /f /IM chromedriver.exe >nul 2>&1")
