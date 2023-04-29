from db_utils import QueryAll
import pandas as pd
import statsmodels.api as sm
import dateutil
from ast import literal_eval


columns = ["id", "url", "location", "brand", "model", "screenSize", "storage", "postage", "shippingType", 
          "endTime", "returnsAccepted", "returnsDays", "condition", "sellerFeedbackScore", "sellerPositivePercent", 
          "sellerName", "price", "bids", "ram", "resolution", "sellerPositive", "sellerNegative", "quantity", 
          "sellerItemsSold", "sellerRecordedFeedback"]
data = pd.DataFrame(QueryAll())
data.columns = columns


# The ```isPolice``` column identifies whether a listing is sold by a police auctioneer.

data["isPolice"] = (data.sellerName == "leicester_police_property_disposa...") | (data.sellerName == "sussexpolice-auctions")
data.isPolice = data.isPolice.astype(int)


# The ```ram``` column specifies the memory of the device sold, in gigabytes. Any listings with recorded RAM higher than 10 GB are treated as missing values, as those sellers mistakenly thought memory meant storage.

data.ram = data.ram.astype(float)
data.loc[data.ram > 10, "ram"] = -1


# The ```storage``` column specifies the storage of the device sold, in gigabytes. Here it is casted to integers.

data.storage = data.storage.astype(int)


# The ```sellerLifePercent``` column stores the percentage of positive feedback received by the seller of a listing throughout their time on eBay. The ```sellerYearPercent``` stores this percentage restricted to listings sold within the past year.

data.sellerPositive = data.sellerPositive.astype(str).str.replace(",","").astype(int)
data.sellerNegative = data.sellerNegative.astype(str).str.replace(",","").astype(int)


data["sellerLifePercent"] = data.sellerPositivePercent.str.replace("%","").astype(float)
data["sellerYearPercent"] = data.sellerPositive/(data.sellerPositive+data.sellerNegative).astype(float)*100
data.sellerYearPercent = data.sellerYearPercent.round()
data.loc[data.sellerYearPercent.isna(), "sellerYearPercent"] = 0


# The ```brand``` and ```model``` columns contain specifications of the device, and here all whitespaces are removed and text made lower case.

data.brand = data.brand.str.lower().str.strip()
data.model = data.model.str.lower().str.strip()


# The brands of listings are converted to dummy variables for major brands present.

data["apple"] = (data.brand == "apple").astype(int)
data["samsung"] = (data.brand == "samsung").astype(int)
data["amazon"] = (data.brand == "amazon").astype(int)
data["others"] = ((data.brand != "apple") & (data.brand != "samsung") & (data.brand != "amazon")).astype(int)


# The ```sellerItemsSold``` column stores the total number of listings sold by the seller.

def repl(num):
    n = num.group(0)
    if "K" in n:
        if "." in n:
            return n.replace(".","").replace("K","") + "00"
        else:
            return n.replace("K","") + "000"
    elif "M" in n:
        if "." in n:
            return n.replace(".","").replace("M","") + "00000"
        else:
            return n.replace("M","") + "000000"
    
data.sellerItemsSold = data.sellerItemsSold.astype(str).str.replace("[0-9,.]+(M|K)", repl, regex=True).astype(int)


# The ```postage``` column stores the cost of shipping of the listing. Free postage is recorded as 0.

def transform_p(po):
    p = str(po)
    if p == "Free" or p == "0":
        return 0
    elif p.startswith("£"):
        return p[1:]
    elif p.startswith("EUR"):
        return float(p[4:])*0.88

data.postage = data.postage.apply(transform_p)


# The ```isUsed``` column specifies if the device sold is brand new or used. The ```isBroken``` column specifies if it is partly not working. 

data["isUsed"] = (data.condition == "Used") | (data.condition == "For parts or not working") \
    | (data.condition == "Good - Refurbished")
data["isBroken"] = (data.condition == "For parts or not working")
data.isUsed = data.isUsed.astype(int)
data.isBroken = data.isBroken.astype(int)


# The ```deliverySpeed``` column specifies the speed of the postage service used by the seller, labeled from 0 to 2, where 0 is the slowest (economy) and 2 is the fastest (express or courier).

def transform_d(de):
    if de == "Economy Delivery" or de == "An Post International" or de =="Free collection in person":
        return 0
    elif de == "Standard Delivery":
        return 1
    elif de == "Express Delivery" or de == "Courier":
        return 2

data["deliverySpeed"] = data.shippingType.apply(transform_d)


# The ```startingPrice``` column stores the minimum price set by the seller. This includes the postage.

def transform_s(row):
    b = eval(row.bids)
    _b = b[-1].replace(",","")
    if _b.startswith("£"):
        return float(b[-1][1:])+float(row.postage)
    elif _b.startswith("EUR"):
        return float(b[-1][4:])*0.88+float(row.postage)
    
data["startingPrice"] = data.apply(transform_s, axis=1)


# The ```bids``` column contains arrays of highest bids made by distinct bidders, in descending order. It contains the winning price but not the minimum price, all inclusive of the postage.

def transform_b(row):
    b = eval(row.bids)[:-1]
    _bids = []
    for bid in b:
        _bid = bid.replace(",","")
        if bid.startswith("£"):
            _bids.append(_bid[1:])
        elif bid.startswith("EUR"):
            _bids.append(float(_bid[4:])*0.88)
        
    bids_with_postage = [float(bid) + float(row.postage) for bid in _bids]
    return bids_with_postage

data.bids = data.apply(transform_b, axis=1)


# The ```isSold``` column indicates whether a listing received at least one bid.

data["isSold"] = data.bids.astype(bool).astype(int)


# The ```price``` column records the transaction price of the listing. It is not the highest bid but an increment of the second highest, as per eBay rules. This includes the postage.

def transform_pr(row):
    p = str(row.price)
    _p = p.replace(",","")
    if p.startswith("£"):
        return float(_p[1:])+float(row.postage)
    elif p.startswith("EUR"):
        return float(_p[4:])*0.88+float(row.postage)

data.price = data.apply(transform_pr, axis=1)


# Here, all price related columns are adjusted for the quantity of devices sold within each listing.

def transform_q(row):
    row.bids = [round(float(bid)/row.quantity, 2) for bid in row.bids]
    row.startingPrice = round(float(row.startingPrice)/row.quantity, 2)
    row.price = round(float(row.price)/row.quantity, 2)
    return row
    
data = data.apply(transform_q, axis=1)


# The ```bidCount``` column stores the number of bids a auction received.

data["bidCount"] = data.bids.apply(lambda a: len(a))


# The ```isNight``` column stores whether an auction ended during night time, defined as being after 5PM and before 2AM.

tzmapping = {"GMT": dateutil.tz.gettz("Europe/London"),
             "BST": dateutil.tz.gettz("Europe/London")}

data.endTime = data.endTime.apply(dateutil.parser.parse, tzinfos=tzmapping).dt.tz_convert("UTC")

data.endTime = pd.to_datetime(data.endTime)
data["isNight"] = ((data.endTime.dt.hour > 16) | (data.endTime.dt.hour < 2)).astype(int)


data.sellerRecordedFeedback = data.sellerRecordedFeedback.astype(str).str.replace(",","").astype(int)


X = data[data["sellerFeedbackScore"] >= 0]["sellerRecordedFeedback"]
y = data[data["sellerFeedbackScore"] >= 0]["sellerFeedbackScore"]

exog = sm.add_constant(X)

result = sm.OLS(y,exog).fit()

data.loc[data[data["sellerFeedbackScore"] == -1].index,"sellerFeedbackScore"] = \
data[data["sellerFeedbackScore"] == -1].sellerRecordedFeedback.apply(lambda n: result.predict([1,n])[0])


# The data is exported as a ```.csv``` file for further analysis.

keep = ["id", "apple", "samsung", "amazon", "others", "model", "screenSize", "storage", "isNight", "returnsAccepted", "returnsDays", 
           "sellerFeedbackScore", "bids", "price", "ram", "resolution", "sellerItemsSold", "isPolice", "sellerLifePercent",
           "sellerYearPercent", "isUsed", "isBroken", "deliverySpeed", "startingPrice", "isSold", "endTime", "bidCount"]
data = data[keep]


data.to_csv("../data/listings.csv", index=False)



# Extract individual bids

data = pd.read_csv("../data/listings.csv")

data = data.drop(data[data["isSold"] == 0].index).reset_index(drop=True)

top_two = data.bids.apply(lambda x: eval(x)[:2])

def EBAY_INCREMENT(current):
    if current < 1:
        return 0.05
    elif current < 5:
        return 0.2
    elif current < 15:
        return 0.5
    elif current < 60:
        return 1
    elif current < 150:
        return 2
    elif current < 300:
        return 5
    elif current < 600:
        return 10
    elif current < 1500:
        return 20
    elif current < 3000:
        return 50
    else:
        return 100
    
def INTERVALS(current):
    if current < 1:
        return 1
    elif current < 5:
        return 5
    elif current < 15:
        return 15
    elif current < 60:
        return 60
    elif current < 150:
        return 150
    elif current < 300:
        return 300
    elif current < 600:
        return 600
    elif current < 1500:
        return 1500
    elif current < 3000:
        return 3000
    

def rule_used(bids):
    increment = EBAY_INCREMENT(bids[-1])
    if bids[0]-bids[-1] != increment:
        return 0
    else:
        return 1

data["ruleTriggered"] = top_two.apply(rule_used)
data["increment"] = data.bids.apply(lambda x: eval(x)[0]+EBAY_INCREMENT(eval(x)[0]))
data.increment = data.increment.astype(float)


data.bids = data.bids.apply(literal_eval)


new_data = data.explode("bids").reset_index(drop=True)


def get_order(row):
    _id = row.id
    bid = row.bids
    original_bids = data[data.id == _id].bids.iloc[0]
    return original_bids.index(bid)+1

new_data["nobid"] = new_data.apply(get_order, axis=1)


for _id in new_data["id"].unique():
    listing = new_data[new_data["id"] == _id]
    for index, count in zip(list(listing["nobid"].value_counts().index), listing["nobid"].value_counts().values):
        for i in range(count-1):
            for j in range(i+1):
                l = new_data[(new_data["id"] == _id) & (new_data["nobid"] == index)].index[0]
                new_data.iloc[l,-1] = new_data.iloc[l,-1] + j + 1


apple = new_data[new_data.apple == 1]
samsung = new_data[new_data.samsung == 1]
amazon = new_data[new_data.amazon == 1]
others = new_data[new_data.others == 1]

new_data.loc[apple.index,["bids","startingPrice", "price", "increment"]] = (apple[["bids","startingPrice", "price", "increment"]]/apple.bids.std())
new_data.loc[samsung.index,["bids","startingPrice", "price", "increment"]] = (samsung[["bids","startingPrice", "price", "increment"]]/samsung.bids.std())
new_data.loc[amazon.index,["bids","startingPrice", "price", "increment"]] = (amazon[["bids","startingPrice", "price", "increment"]]/amazon.bids.std())
new_data.loc[others.index,["bids","startingPrice", "price", "increment"]] = (others[["bids","startingPrice", "price", "increment"]]/others.bids.std())


new_data.to_csv("../data/bids.csv", index=False)