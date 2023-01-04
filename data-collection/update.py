from db_utils import QueryEmpty, UpdateItem, ClearOne
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Instantiate a Chrome driver
chrome_options = Options()
chrome_options.headless = False
driver = webdriver.Chrome(options=chrome_options)


# Get all unfilled listings in database
listings = QueryEmpty()
print(f'Listings to fill in: {len(listings)}')


# Columns that need to be manually filled in
COLS = ["brand", "model", "screenSize", "storage", "returnsAccepted", "returnsDays",
     "ram", "resolution", "quantity"]


# For each listing, manually populate details of its specifications
for listing in listings:
    dict_ = dict()

    url = listing[4]
    driver.get(url)

    # Define a prompt function that can be recursively called
    def prompt(label, id):
        col_res = input(f'{col}: ')

        # If the input is "NO", ignore the listing for later
        if col_res == 'NO':
            raise Exception('listing ignored for now')
        # If the input is "DISCARD", delete the listing
        elif col_res == 'DISCARD':
            ClearOne(id)
            raise Exception('listing deleted')
        # Raise the prompt again until there is valid input
        elif col_res == '':
            prompt(label, id)
        return col_res

    # Collect data for each unfilled column
    for col in COLS:
        try:
            dict_[col] = prompt(col, listing[0])
        except Exception as e:
            print(e)
            break

    # Once navigated to bids page, automatically collect every unique bidder's highest bid
    else:
        try:
            l = driver.find_element(By.CSS_SELECTOR, "#vi-VR-bid-lnk-")
            elements = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr > td:first-child > .textual-display-item > span > span:first-child"))
            )
            bidders = [el.get_attribute("innerText").replace('Highest bidder\n', '') for el in elements]
            unique = [bidders.index(x) for x in set(bidders)]
            unique.sort()

            bid_els = driver.find_elements(By.CSS_SELECTOR, "tr > td:nth-child(2) > div > span > span")
            bids_ = [el.get_attribute("innerText") for el in bid_els]
            bids = [bids_[i] for i in unique]

            dict_["bids"] = f'{bids}'

            UpdateItem(listing[0], dict_) 
        except Exception as e:
            print(e)
            bid_el = driver.find_element(By.CSS_SELECTOR, "#prcIsum, .vi-VR-cvipPrice")
            bid = bid_el.get_attribute("innerText")

            dict_["bids"] = f'{[bid]}'

            UpdateItem(listing[0], dict_) 
        
        
# Close the driver
driver.close()