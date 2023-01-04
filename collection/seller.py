from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db_utils import Query, UpdateItem
import re

chrome_options = Options()
chrome_options.headless = False
driver = webdriver.Chrome(options=chrome_options)

listings = Query("SELECT * FROM listings WHERE sellerItemsSold is null")
sellers = set([listing[-9] for listing in listings])

dict_ = {}

for idx, seller in enumerate(sellers):
    if seller == "leicester_police_property_disposa...":
        driver.get("https://www.ebay.co.uk/str/leicesterpolicepropertydisposal")
    else:
        driver.get(f"https://ebay.co.uk/usr/{seller}")

    sold_el = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".str-seller-card__stats-content > div:nth-child(2) > span"))
    )
    sold = sold_el.get_attribute("innerText")

    percent_el = driver.find_element(By.CSS_SELECTOR, ".str-seller-card__feedback-link > span")
    percent = percent_el.get_attribute("innerText")
    
    try:
        total_el = driver.find_element(By.CSS_SELECTOR, ".str-seller-card__feedback-link")
        total = re.search("(?<=\()[0-9]+(?=\))", total_el.get_attribute("innerText")).group(0)
    except:
        total = -1

    positive_el = driver.find_element(By.CSS_SELECTOR, ".fdbk-overall-rating__details > div:nth-child(1) > a > span")
    positive = positive_el.get_attribute("innerText")

    neutral_el = driver.find_element(By.CSS_SELECTOR, ".fdbk-overall-rating__details > div:nth-child(2) > a > span")
    neutral = neutral_el.get_attribute("innerText")

    negative_el = driver.find_element(By.CSS_SELECTOR, ".fdbk-overall-rating__details > div:nth-child(3) > a > span")
    negative = negative_el.get_attribute("innerText")

    dict_[seller] = [sold, percent, positive, int(neutral.replace(",",""))+int(negative.replace(",","")), total]

    print(f"{idx+1}/{len(sellers)} processed")


for listing in listings:
    try:
        id = listing[0]
        seller = listing[-9]
        params = {
            "sellerItemsSold": dict_[seller][0],
            "sellerPositivePercent": dict_[seller][1],
            "sellerPositive": dict_[seller][2],
            "sellerNegative": dict_[seller][3],
            "sellerFeedbackScore": dict_[seller][4]
        }
        UpdateItem(id, params)
        print(f"updated seller {seller}: {dict_[seller]}")
    except Exception as e:
        print(e)

driver.close()