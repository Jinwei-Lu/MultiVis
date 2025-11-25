import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(0)

varieties = ['Manchuria', 'Glabron', 'No. 475', 'Peatland', 'Svansota', 'Velvet', 'Wisconsin No. 38']
sites = ['Grand Rapids', 'Morris', 'University Farm', 'Waseca', 'Crookston', 'Duluth']

data = []
for variety in varieties:
    for site in sites:
        for _ in range(np.random.randint(1, 5)):
            data.append({
                'variety': variety,
                'site': site,
                'year': np.random.randint(1928, 1932),
                'yield': np.random.randint(20, 50)
            })

source = pd.DataFrame(data)

aggregated_data = source.groupby(['variety', 'site'])['yield'].sum().reset_index()

sites_unique = aggregated_data['site'].unique()

fig, ax = plt.subplots()

y_positions = np.arange(len(varieties))
bar_height = 0.8 / len(sites_unique)

for i, site in enumerate(sites_unique):
    site_data = aggregated_data[aggregated_data['site'] == site]
    variety_y_map = {variety: pos for pos, variety in enumerate(varieties)}
    site_y_positions = [variety_y_map[v] for v in site_data['variety']]

    ax.barh(np.array(site_y_positions) + i * bar_height - (len(sites_unique) - 1) * bar_height / 2,
            site_data['yield'],
            height=bar_height,
            label=site)

ax.set_yticks(y_positions)
ax.set_yticklabels(varieties)
ax.set_xlabel('sum(yield)')
ax.set_ylabel('variety')
ax.legend()
ax.invert_yaxis()

plt.show()