from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Instantiate a Chrome driver
chrome_options = Options()
chrome_options.headless = True
driver = webdriver.Chrome(options=chrome_options)


# URLs to police auction pages containing tablets 
SUSSEX_POLICE = "https://www.ebay.co.uk/sch/171485/i.html?_nkw=&_in_kw=1&_ex_kw=&LH_Complete=1&_udlo=&_udhi=&LH_Auction=1&_ftrt=901&_ftrv=1&_sabdlo=&_sabdhi=&_samilow=&_samihi=&_sadis=15&_stpos=EC4Y0DF&_sargn=-1%26saslc%3D1&_salic=3&_fss=1&_fsradio=%26LH_SpecificSeller%3D1&_saslop=1&_sasl=sussexpolice-auctions&_sop=13&_dmd=1&_ipg=60"
LEICESTER_POLICE = "https://www.ebay.co.uk/sch/171485/i.html?_nkw=&_in_kw=1&_ex_kw=&LH_Complete=1&_udlo=&_udhi=&LH_Auction=1&_ftrt=901&_ftrv=1&_sabdlo=&_sabdhi=&_samilow=&_samihi=&_sadis=15&_stpos=EC4Y0DF&_sargn=-1%26saslc%3D1&_salic=3&_fss=1&_fsradio=%26LH_SpecificSeller%3D1&_saslop=1&_sasl=leicester_police_property_disposals&_sop=13&_dmd=1&_ipg=60"


# Get the title of all tablet listings from Sussex Police, and combine in a file
driver.get(SUSSEX_POLICE)
title_els = driver.find_elements(By.CSS_SELECTOR, ".s-item__title > span")

with open('policeauctions.txt', 'a') as f:
    for el in title_els[1:]:
        f.write(f'{el.get_attribute("innerText")}\n')


# Get the title of all tablet listings from Leicester Police, and combine in a file
driver.get(LEICESTER_POLICE)
title_els = driver.find_elements(By.CSS_SELECTOR, ".s-item__title > span")

with open('policeauctions.txt', 'a') as f:
    for el in title_els[1:]:
        f.write(f'{el.get_attribute("innerText")}\n')


# Close the driver
driver.close()


# Remove any duplicated listings
with open("policeauctions.txt", "r") as f:
    seen = []
    lines = []

    for line in f:
        if line not in seen:
            lines.append(line)
            seen.append(line)
        else:
            print(f'removing {line}')

with open("policeauctions.txt", "w") as f:
    for line in lines:
        f.write(line)