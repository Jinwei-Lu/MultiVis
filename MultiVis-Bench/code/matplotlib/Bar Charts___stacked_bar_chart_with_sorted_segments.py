import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)

n_varieties = 3
n_sites = 6
n_years = 2

varieties = [f'Variety_{i+1}' for i in range(n_varieties)]
sites = [f'Site_{i+1}' for i in range(n_sites)]
years = [2022, 2023]

data = []
for variety in varieties:
    for site in sites:
      for year in years:
        data.append({'variety': variety, 'site': site, 'year': year, 'yield': np.random.randint(10, 50)})

source = pd.DataFrame(data)

agg_data = source.groupby(['variety', 'site'])['yield'].sum().reset_index()

fig, ax = plt.subplots()

unique_sites = agg_data['site'].unique()
unique_varieties = agg_data['variety'].unique()

sorted_sites = sorted(unique_sites)

bottom = np.zeros(len(unique_varieties))

for i, site in enumerate(sorted_sites):
    site_data = agg_data[agg_data['site'] == site]

    variety_order = pd.DataFrame({'variety': unique_varieties})
    site_data = pd.merge(variety_order, site_data, on='variety', how='left')
    site_data = site_data.fillna(0)

    ax.barh(site_data['variety'], site_data['yield'], left=bottom, label=site)
    bottom += site_data['yield'].values

ax.legend()
plt.show()