from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_score(look_for):
    """
    :param look_for: exact name of film you look for
    :return: scrapped score of film on CSFD
    """
    options = Options()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)
    driver.get(f"https://www.google.com/search?q={look_for}")

    try:
         cookie = WebDriverWait(driver, 10).until(
             EC.presence_of_element_located((By.XPATH, '//*[@id="W0wltc"]/div'))
         )
         cookies = driver.find_element(By.XPATH, '//*[@id="W0wltc"]/div').click()
         rating = driver.find_element(By.XPATH,
                                     '//*[@id="rso"]/div[1]/div/div/div[1]/div/div/div[4]/div/span[1]').text.strip("%Hodnocení: ")
         print(rating)
    finally:
        driver.quit()
    return rating

find_score("matrix")
