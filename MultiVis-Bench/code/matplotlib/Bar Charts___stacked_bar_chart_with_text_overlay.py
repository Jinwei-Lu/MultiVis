import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
varieties = ['A', 'B', 'C', 'D', 'E']
sites = ['Site1', 'Site2', 'Site3']
data = []
for variety in varieties:
    for site in sites:
        data.append({'variety': variety, 'site': site, 'yield': np.random.randint(10, 50)})
source = pd.DataFrame(data)

fig, ax = plt.subplots()

cumulative_yield = source.groupby(['variety', 'site'])['yield'].sum().unstack(fill_value=0)
bottom = np.zeros(len(varieties))

for i, site in enumerate(sites):
    widths = cumulative_yield[site].values
    starts = bottom
    rects = ax.barh(varieties, widths, left=starts, height=0.8, label=site)

    bottom += widths

ax.set_xlabel('Sum of Yield')
ax.set_ylabel('Variety')
ax.legend()

plt.show()