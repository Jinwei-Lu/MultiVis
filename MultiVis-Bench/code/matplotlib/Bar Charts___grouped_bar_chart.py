import matplotlib.pyplot as plt
import numpy as np

years = ['1930', '1931', '1932']
sites = ['Site A', 'Site B', 'Site C', 'Site D']

np.random.seed(0)
yield_data = {}
for site in sites:
    yield_data[site] = {}
    for year in years:
        yield_data[site][year] = np.random.randint(50, 200)

fig, axes = plt.subplots(1, len(sites), sharey=True)

for i, site in enumerate(sites):
    ax = axes[i]
    x_positions = np.arange(len(years))
    bar_width = 0.7

    for j, year in enumerate(years):
        ax.bar(x_positions[j], yield_data[site][year], width=bar_width)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(years)

axes[0].legend()

plt.show()