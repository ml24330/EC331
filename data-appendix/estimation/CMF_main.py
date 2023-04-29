import sys
import pandas as pd

sys.path.append('../')

from functions import *

data = pd.read_csv("../../data/demeaned.csv")
df = data.groupby(["id", "ispolice", "sellerfeedbackscore", "bidcount", "apple", "amazon", "increment_residual"])["residual"].apply(lambda x: x.values).reset_index()

valid_bids = list(df[df.ispolice == 1].bidcount.value_counts().index)
include = df[(df.bidcount > 1) & (df.bidcount.isin(valid_bids))]

bids = list(include.residual)

logged_feedback = np.log(include.sellerfeedbackscore+1)
logged_feedback = transform_covariates(logged_feedback, 100)
include.sellerfeedbackscore = logged_feedback

covariates = np.array(include[["ispolice", "sellerfeedbackscore"]])
covariates = list([list(cov) for cov in covariates])
incremented = list(include.increment_residual)

median_upper, median_lower = estimate_median(bids, covariates, incremented, (-4,6))
dump(median_lower, median_upper, "CMF_main")

bootstrap(bids, covariates, incremented, [], [], 40, "main")