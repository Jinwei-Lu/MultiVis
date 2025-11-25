import matplotlib.pyplot as plt
import numpy as np

varieties = ['Wisconsin No. 38', 'Velvet', 'Trebi', 'Svansota', 'Peatland', 'No. 475', 'No. 462', 'No. 457', 'Manchuria', 'Glabron']
sites = ['Waseca', 'University Farm', 'Morris', 'Grand Rapids', 'Duluth', 'Crookston']
years = ['1931', '1932']
num_varieties = len(varieties)
num_sites = len(sites)

rng = np.random.default_rng(42)

yield_data = {}
for year in years:
    yield_data[year] = {}
    for variety in varieties:
        yield_data[year][variety] = rng.integers(0, 60, size=num_sites)

fig, axes = plt.subplots(1, 2, sharey=True)

for i, year in enumerate(years):
    ax = axes[i]
    bottom = np.zeros(num_varieties)

    for j, site in enumerate(sites):
        site_yields = [yield_data[year][variety][j] for variety in varieties]
        ax.barh(varieties, site_yields, left=bottom)
        bottom += np.array(site_yields)

    ax.set_xlabel('yield')
    if i == 0:
        ax.set_ylabel('variety')

handles, labels = axes[1].get_legend_handles_labels()
fig.legend(handles, labels)

plt.show()