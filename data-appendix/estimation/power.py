import pandas as pd
import numpy as np
from scipy import stats
from functions import *
from ast import literal_eval

data = pd.read_csv("../data/bids.csv")
df = data.groupby(["id", "ruleTriggered", "sellerFeedbackScore", "bidCount"])["bids"].apply(lambda x: x.values).reset_index()
P_JUMP = 1 - df.ruleTriggered.mean()

df.sellerFeedbackScore = np.log(df.sellerFeedbackScore+1)
mean = df.sellerFeedbackScore.mean()
std = df.sellerFeedbackScore.std()

max_bidcount = df.bidCount.max()

def EBAY_INCREMENT(current):
    if current < 1:
        return current + 0.05
    elif current < 5:
        return current + 0.2
    elif current < 15:
        return current + 0.5
    elif current < 60:
        return current + 1
    elif current < 150:
        return current + 2
    elif current < 300:
        return current + 5
    elif current < 600:
        return current + 10
    elif current < 1500:
        return current + 20
    elif current < 3000:
        return current + 50
    else:
        return current + 100
    

def bid(CURRENT_PRICE, ACTIVE_BIDDERS, INCREMENT, HISTORY, P_JUMP):
    if len(ACTIVE_BIDDERS) < 2:
        return HISTORY
    else:
        POSSIBLE_BIDDERS = ACTIVE_BIDDERS[:]
        if HISTORY:
            POSSIBLE_BIDDERS.remove(HISTORY[-1]["bidder"])
        bidder = POSSIBLE_BIDDERS[np.random.randint(len(POSSIBLE_BIDDERS))]
        if bidder < INCREMENT(CURRENT_PRICE):
            ACTIVE_BIDDERS.remove(bidder)
            return bid(CURRENT_PRICE, ACTIVE_BIDDERS, INCREMENT, HISTORY, P_JUMP)
        else:
            jump = np.random.random() < P_JUMP
            
            if jump:
                new_bid = np.random.uniform(INCREMENT(CURRENT_PRICE), bidder)
            else:
                new_bid = INCREMENT(CURRENT_PRICE)
                
            HISTORY.append({
                "bidder": bidder,
                "bid": new_bid
            })
                
            return bid(new_bid, ACTIVE_BIDDERS, INCREMENT, HISTORY, P_JUMP)

def simulate(VALUES, INCREMENT, P_JUMP, SILENT=1):
    BIDDERS = [round(bidder, 2) for bidder in VALUES]
    
    result = bid(0, BIDDERS, INCREMENT, [], P_JUMP)
    
    recorded_bids = {}
    for b in result:
        recorded_bids[b["bidder"]] = b["bid"]
        recorded_bids = dict(sorted(recorded_bids.items(), key=lambda item: item[1]))
    
    if not SILENT:
        print("The auction has ended.")
        print(f"There were {len(VALUES)} potential bidders, and {len(recorded_bids)} of them submitted bids.")
        print(f"{len(result)} rounds of bidding occured.")
        print(f"The recorded bids are as follows:")

        for bidder, _bid in recorded_bids.items():
            print(f"The final bid of {bidder} is {_bid}.")

    return list(recorded_bids.values())


def estimate(N):
    for j in range(3):
        feedbacks = stats.lognorm.rvs(loc=mean, scale=std, s=1, size=N)
        include = pd.DataFrame()

        for feedback in feedbacks:
            valuations = stats.norm.rvs(loc=feedback*0.5, scale=1, size=max_bidcount)
            bids = simulate(valuations, EBAY_INCREMENT, P_JUMP)
            bidcount = len(bids)
            include = pd.concat([include, pd.DataFrame([[feedback, bids, bidcount]])])

        include.columns = ["feedback", "bid", "bidcount"]

        keep = include.bidcount.value_counts().values > 2
        valid_bids = include.bidcount.value_counts()[keep].index

        include = include[include.bidcount.isin(valid_bids)]

        bids = list(include.bid)
        covariates = [[cov] for cov in list(include.feedback)]

        covariates = [[round(cov, 5)] for cov in transform_covariates([cov[0] for cov in covariates],100)]

        incremented = [EBAY_INCREMENT(b[-1]) for b in bids]

        max_support = round(include.explode("bid").bid.max())

        cef = lambda c, cov: c[0]*cov[0]
        n_cov = 1

        results = bootstrap2(bids, covariates, incremented, (0,max_support), [n_cov], [cef], 10, f"power_{N}_{j}")

        a_lower, a_upper = [[a[i] for a in results[0]] for i in range(2)]
        
        print(f"calculated {j+1}/10 estimates for simulations containing {N} total auctions")
        print(f"a cf: [{np.percentile(a_lower, 5)}, {np.percentile(a_upper, 95)}]")
        

for N in [250,500,1000,2500]:
    estimate(N)