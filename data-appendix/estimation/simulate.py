import pandas as pd
import numpy as np
from scipy import optimize, stats
import seaborn as sns
from statsmodels.nonparametric import kernel_regression

data = pd.read_csv("../data/demeaned.csv")
df = data.groupby(["id", "ispolice", "sellerfeedbackscore", "bidcount", "apple", "amazon", "increment_residual"])["residual"].apply(lambda x: x.values).reset_index()
valid_bids = list(df[(df.ispolice == 1) & (df.bidcount > 1)].bidcount.value_counts().index)
include = df[df.bidcount.isin(valid_bids)]

include.sellerfeedbackscore = np.log(include.sellerfeedbackscore+1)
nonpolice = include[include.ispolice == 0]
ispolice = include[include.ispolice == 1]


nonpolice_dict = {}
police_dict = {}

def get_tuple(row):
    return (row.sellerfeedbackscore, row.residual)

for i in valid_bids:
    nonpolice_dict[f"{i}"] = list(nonpolice[nonpolice.bidcount == i].explode("residual").reset_index(drop=True).apply(get_tuple, axis=1))
    police_dict[f"{i}"] = list(ispolice[ispolice.bidcount == i].explode("residual").reset_index(drop=True).apply(get_tuple, axis=1))


fits = {}

l = ispolice.explode("residual")
l.residual = l.residual.astype(float)
police_cov = np.cov(l.residual, l.sellerfeedbackscore)[0][1]


for i in valid_bids:
    tuples = nonpolice_dict[f"{i}"]
    x = np.array([t[0] for t in tuples])
    y = np.array([t[1] for t in tuples])
    
    police_x = np.array([t[0] for t in police_dict[f"{i}"]])
    police_y = np.array([t[1] for t in police_dict[f"{i}"]])
    
    
    non_x0 = x.mean()
    non_x_sig = x.var()
    non_cov = np.cov(x,y)[0][1]
    police_y0 = police_y.mean()
    police_y_sig = police_y.var()
    cov = np.array([[non_x_sig, police_cov], [police_cov, police_y_sig]])
    
    min_eig = np.min(np.real(np.linalg.eigvals(cov)))
    if min_eig < 0:
        cov -= 10*min_eig * np.eye(*cov.shape)
    
    normal_fit = stats.multivariate_normal(mean=[non_x0, police_y0], cov=cov)
    
    fits[f"{i}"] = normal_fit

#     marginal = lambda x: normal_fit.pdf([9.95527731, x])
    
#     values = np.linspace(-5,5,num=100)
#     plt.hist(police_y, bins=10, weights=[1/len(police_y)]*len(police_y))
#     plt.plot(values, [marginal(v) for v in values])
#     plt.title(f"{i} bids")
#     plt.show()
    

def get_dist(joint_rv, x):
    mean = joint_rv.mean[1] + joint_rv.cov[1][0] * (1 / joint_rv.cov[0][0]) * (x - joint_rv.mean[0])
    var = joint_rv.cov[1][1] - (joint_rv.cov[1][0]**2) * (1 / joint_rv.cov[0][0])
    return stats.norm(loc=mean, scale=var**0.5)

df2 = pd.DataFrame(columns=["sellerfeedbackscore", "increment_residual", "residual", "bidcount"])
cols = ["sellerfeedbackscore", "increment_residual", "residual", "bidcount", "ispolice"]

for i in valid_bids:
    feedbacks = list(nonpolice[nonpolice.bidcount == i].sellerfeedbackscore)
    fit = fits[f"{i}"]
    simulated = [(f, -1, sorted(get_dist(fit, f).rvs(size=i))[::-1], i, 1) for f in feedbacks]
    
    new_df = pd.DataFrame(simulated, columns=cols)
    df2 = pd.concat([df2, new_df])
    
df2 = pd.concat([df2, nonpolice[cols]])


exog = df2[df2.increment_residual != -1].residual.apply(lambda x: x[0])
endog = df2[df2.increment_residual != -1].increment_residual.astype(float)

model = kernel_regression.KernelReg(endog, exog, "c")

def impute(row):
    if row.increment_residual != -1:
        return row.increment_residual
    else:
        return model.fit([row.residual[0]])[0][0]

df2.increment_residual = df2.apply(impute, axis=1)


df2.to_csv("../data/simulated.csv", index=False)