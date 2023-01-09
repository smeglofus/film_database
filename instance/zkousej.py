import requests

from main import *

from bs4 import BeautifulSoup
import re



options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_experimental_option("detach", True)
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
driver.get(f"https://www.google.com/search?q=avatar+2022+csfd")
cookie = WebDriverWait(driver, 3).until(
             EC.presence_of_element_located((By.XPATH, '//*[@id="W0wltc"]/div'))
         )
cookies = driver.find_element(By.XPATH, '//*[@id="W0wltc"]/div').click()
source = driver.page_source
word = "Hodnocení"
if word in source:
    index = source.index("Hodnocení")
    print(source[index+11:index+13])
