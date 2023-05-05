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

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update(matplotlib.rcParamsDefault)
plt.style.use('tableau-colorblind10')
plt.rcParams['figure.figsize'] = (8,8)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['text.color'] = 'black'
plt.rcParams['axes.labelcolor'] = 'black'
plt.rcParams['xtick.color'] = 'black'
plt.rcParams['ytick.color'] = 'black'
plt.rcParams['axes.titlepad'] = 5
plt.rcParams['axes.titlesize'] = 9
plt.rcParams['axes.labelsize'] = 8
plt.rcParams['axes.labelpad'] = 5
plt.rcParams['legend.fontsize'] = 7
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.facecolor'] = 'white'

include = df

bids = list(include.residual)

logged_feedback = include.sellerfeedbackscore
logged_feedback = transform_covariates(logged_feedback, 100)
include.sellerfeedbackscore = logged_feedback

covariates = np.array(include[["ispolice", "sellerfeedbackscore"]])
covariates = list([list(cov) for cov in covariates])
incremented = list(include.increment_residual)

pdfs, pdfs_delta = get_order_statistic_pdfs(bids, covariates, incremented)

_min = np.percentile([c[1] for c in covariates], 10)
median = np.percentile([c[1] for c in covariates], 50)
_max = np.percentile([c[1] for c in covariates], 90)

n_upper_med, n_lower_med = get_estimated_distributions(pdfs, pdfs_delta, [0, median], (-4,6))
p_upper_med, p_lower_med = get_estimated_distributions(pdfs, pdfs_delta, [1, median], (-4,6))

n_upper_min, n_lower_min = get_estimated_distributions(pdfs, pdfs_delta, [0, _min], (-4,6))
p_upper_min, p_lower_min = get_estimated_distributions(pdfs, pdfs_delta, [1, _min], (-4,6))

n_upper_max, n_lower_max = get_estimated_distributions(pdfs, pdfs_delta, [0, _max], (-4,6))
p_upper_max, p_lower_max = get_estimated_distributions(pdfs, pdfs_delta, [1, _max], (-4,6))

values = np.linspace(-3,3,num=35)

n_upper_vals_med = [n_upper_med(v,-1) for v in values]
n_lower_vals_med = [n_lower_med(v,1) for v in values]

p_upper_vals_med = [p_upper_med(v,-1) for v in values]
p_lower_vals_med = [p_lower_med(v,1) for v in values]


n_upper_vals_min = [n_upper_min(v,-1) for v in values]
n_lower_vals_min = [n_lower_min(v,1) for v in values]

p_upper_vals_min = [p_upper_min(v,-1) for v in values]
p_lower_vals_min = [p_lower_min(v,1) for v in values]


n_upper_vals_max = [n_upper_max(v,-1) for v in values]
n_lower_vals_max = [n_lower_max(v,1) for v in values]

p_upper_vals_max = [p_upper_max(v,-1) for v in values]
p_lower_vals_max = [p_lower_max(v,1) for v in values]

fig, (ax1, ax2, ax3) = plt.subplots(3,1, constrained_layout=True)

ax1.plot(values, n_upper_vals_min, label="Non-police upper bound", color="red")
ax1.plot(values, n_lower_vals_min, label="Non-police lower bound", color="red", linestyle="--")

ax1.plot(values, p_upper_vals_min, label="Police upper bound", color="blue")
ax1.plot(values, p_lower_vals_min, label="Police lower bound", color="blue", linestyle="--")

ax1.set_xlim(-3,3)
ax1.set_title("10th Percentile")

ax2.plot(values, n_upper_vals_med, label="Non-police upper bound", color="red")
ax2.plot(values, n_lower_vals_med, label="Non-police lower bound", color="red", linestyle="--")

ax2.plot(values, p_upper_vals_med, label="Police upper bound", color="blue")
ax2.plot(values, p_lower_vals_med, label="Police lower bound", color="blue", linestyle="--")

ax2.set_ylabel("Cumulative probability")
ax2.set_title("Median")
ax2.legend(loc="lower right")

ax2.set_xlim(-3,3)

ax3.plot(values, n_upper_vals_max, label="Non-police upper bound", color="red")
ax3.plot(values, n_lower_vals_max, label="Non-police lower bound", color="red", linestyle="--")

ax3.plot(values, p_upper_vals_max, label="Police upper bound", color="blue")
ax3.plot(values, p_lower_vals_max, label="Police lower bound", color="blue", linestyle="--")

ax3.set_xlabel("(Normalised) Willingness to pay")
ax3.set_title("90th Percentile")

ax3.set_xlim(-3,3)

fig.savefig("bounds.png", dpi=fig.dpi, bbox_inches="tight")
