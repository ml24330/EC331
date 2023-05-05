import pandas as pd

df = pd.read_csv("../../data/demeaned.csv")
df["time"] = pd.to_datetime(df.endtime).astype(int)
df = df.sort_values("time").reset_index(drop=True)
df = df.groupby(["id", "increment_residual", "time"])["residual"].apply(lambda x: x.values).reset_index()

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update(matplotlib.rcParamsDefault)
plt.style.use('tableau-colorblind10')
plt.rcParams['figure.figsize'] = (8,4)
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

fig, ax = plt.subplots()

ax.plot(df.residual.apply(lambda x: x[-1]))
ax.set_xlabel("Listing Number")
ax.set_ylabel("Homogenised Top Bid")

plt.tight_layout()
fig.savefig("stationarity.png", dpi=fig.dpi, bbox_inches="tight")