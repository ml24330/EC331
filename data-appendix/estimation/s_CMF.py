import sys
import pandas as pd
import re
 
sys.path.append('../')

from functions import *

df = pd.read_csv("../../data/simulated.csv")

def comma(s):
    add_comma = lambda match: match.group(0).replace(" ", ", ")
    
    s = s.replace("\n", "")

    s = re.sub(r"([0-9\.]+\s)", add_comma, s)
    
    return eval(s)

df.residual = df.residual.apply(comma)

include = df

bids = list(include.residual)

logged_feedback = include.sellerfeedbackscore
logged_feedback = transform_covariates(logged_feedback, 100)
include.sellerfeedbackscore = logged_feedback

covariates = np.array(include[["ispolice", "sellerfeedbackscore"]])
covariates = list([list(cov) for cov in covariates])
incremented = list(include.increment_residual)

median_upper, median_lower = estimate_median(bids, covariates, incremented, (-4,6))
dump(median_lower, median_upper, "CMF_s_main")

bootstrap(bids, covariates, incremented, [], [], 40, "s_main")
