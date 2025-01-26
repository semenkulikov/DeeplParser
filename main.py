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
    print("Передвигаю курсор на рандомные точки...")
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
    #  browser.set_page_load_timeout(10)

    set_viewport_size(browser, 1400, 800)

    browser.get("https://www.google.com")
    print(browser.title)

    input_label = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="APjFqb"]')))
    input_label.send_keys("cats")
    input_label.send_keys(Keys.ENTER)

    # click_button('/html/body/div[3]/div[3] ')
    # browser.execute_script("window.scrollTo(0, 100)")  # document.body.scrollHeight)")

    browser.close()

    session = requests.Session()
    page = session.get("https://www.google.com")
    soup = BeautifulSoup(page.text, "html.parser")
    print(soup.find("title").text)

    # h3_tag = soup.findAll("h3")
    # for sub_tag in h3_tag:
    #     for a_tag in sub_tag:
    #         if f"{year}/{str_month}/{str_day}" in a_tag.get("href"):
    #             new_url = unquote(a_tag.get("href"))
    # certain_elem = soup.find("a")
