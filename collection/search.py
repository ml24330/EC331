from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re


# eBay search page URL, filtering only completed auctions

URL = "https://www.ebay.co.uk/sch/i.html?_nkw=test&_in_kw=1&_ex_kw=&_sacat=0&LH_Complete=1&_udlo=&_udhi=&LH_Auction=1&_samilow=&_samihi=&_sadis=15&_stpos=EC4Y0DF&_sargn=-1%26saslc%3D1&_salic=3&_sop=12&_dmd=1&_ipg=60"


# Instantiate a chrome driver

chrome_options = Options()
chrome_options.headless = True
driver = webdriver.Chrome(options=chrome_options)


# Get all relevant titles of police auctions

with open("policeauctions.txt", "r") as f:
    KEYWORDS = [line[:-1] for line in f]


# For each title, record all relevant listings from other accounts suggested by eBay

for keyword in KEYWORDS:
    driver.get(URL)

    input_el = driver.find_element(By.CSS_SELECTOR, "#gh-ac")
    input_el.clear()
    input_el.send_keys(keyword)

    driver.find_element(By.CSS_SELECTOR, "#gh-btn").submit()

    title_els = driver.find_elements(By.CSS_SELECTOR, ".s-item__link")

    with open('matchedauctions.txt', 'a') as f:
        for el in title_els[1:]:
            f.write(f'{el.get_attribute("href")}\n')

driver.close()


# Remove duplicated listings
with open("matchedauctions.txt", "r") as f:
    
    ids = []
    lines = []
    exp = "(?<=itm\/)(.*?)(?=\?)"

    for line in f:
        id = re.search(exp, line).group()
        if id not in ids:
            ids.append(id)
            lines.append(line)
        else:
            print(f'{id} already exists, removing')

with open("matchedauctions.txt", "w") as f:
    for line in lines:
        f.write(line)