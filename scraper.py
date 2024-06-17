# import time
# from selenium.webdriver import Chrome
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium import webdriver

# def returnytcomments(url):
#     data = []

#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument('--headless')  # Optional: Run Chrome in headless mode

#     with Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options) as driver:
#         wait = WebDriverWait(driver, 15)
#         driver.get(url)

#         for item in range(5):
#             wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
#             time.sleep(2)

#         for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#content"))):
#             data.append(comment.text)

#     return data





import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

def returnytcomments(url):
    data = []       

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')  # Optional: Run Chrome in headless mode
    chrome_options.add_argument('--headless')  # Optional: Run Chrome in headless mode
    chrome_options.add_argument('executable_path=C:\Program Files\chromedriver.exe')

    # Set up ChromeDriver using ChromeDriverManager
    # driver_path = ChromeDriverManager().install()

    with Chrome(options=chrome_options) as driver:
        wait = WebDriverWait(driver, 15)
        driver.get(url)

        for item in range(5):
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(2)

        for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#content"))):
            data.append(comment.text)

    return data
