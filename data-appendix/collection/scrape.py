from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from db_utils import InsertListings, Query
import re

# Get the URLs of all matched listings
with open("matchedauctions.txt", "r") as f:
    URLS = [line[:-1] for line in f]


# Create a regex to match item ID from URL
exp = "(?<=itm\/)(.*?)(?=\?)"


# Scrape one listing from eBay
for idx, url in enumerate(URLS):

    # If listing already exists in database, don't scrape
    id = re.search(exp, url).group()
    if len(Query(f'select * from listings where id={id}')) > 0:
        print(f'Item with {id} already exists')
        continue

    # Instantiate a Chrome driver
    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

    # Get the winning bid
    try:
        price_el = driver.find_element(By.CSS_SELECTOR, ".vi-VR-cvipPrice")
        price = price_el.get_attribute("innerText")
    except:
        price = -1

    # Get the condition
    try:
        cond_el = driver.find_element(By.CSS_SELECTOR, "#vi-itm-cond")
        condition = cond_el.get_attribute("innerText")
    except: 
        condition = -1

    # Get the seller's name
    try:
        name_el = driver.find_element(By.CSS_SELECTOR, ".mbg-nw")
        seller_name = name_el.get_attribute("innerText")
    except: 
        seller_name = -1
        
    # Get the postage cost
    try:
        postage_el = driver.find_element(By.CSS_SELECTOR, "#fshippingCost > span")
        postage = postage_el.get_attribute("innerText")
    except:
        postage = -1 

    # Get the shipping time
    try:
        shipping_el = driver.find_element(By.CSS_SELECTOR, "#fShippingSvc")
        shipping = shipping_el.get_attribute("innerText")
    except:
        shipping = -1

    # Get the end time
    try:
        endtime_el = driver.find_element(By.CSS_SELECTOR, "#bb_tlft")
        endtime = endtime_el.get_attribute("innerText")
    except:
        endtime = -1

    driver.close()

    # If a value is undefined, do not insert (this means the seller has hidden details of the listing)
    if endtime != -1:
        InsertListings('id, url, price, condition, sellerName, postage, shippingType, endTime', [(id, url, price, condition, seller_name, postage, shipping, endtime)])
        print(f'Inserted listing with ID {id} ({idx}/{len(URLS)})')
    else:
        print(f'Failed to insert listing with ID {id} ({idx}/{len(URLS)})')

