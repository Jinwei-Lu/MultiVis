import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
varieties = ['A', 'B', 'C']
sites = ['Site1', 'Site2', 'Site3', 'Site4']
data = []
for variety in varieties:
    for site in sites:
        data.append({'variety': variety, 'site': site, 'yield': np.random.randint(20, 80)})

df = pd.DataFrame(data)

fig, ax = plt.subplots()

grouped_data = df.groupby(['variety', 'site'])['yield'].sum().unstack()

bottom = np.zeros(len(varieties))
for i, site in enumerate(sites):
    ax.bar(grouped_data.index, grouped_data[site], bottom=bottom)
    bottom += grouped_data[site].values

ax.legend()

plt.show()