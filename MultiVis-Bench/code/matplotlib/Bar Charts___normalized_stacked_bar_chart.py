import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = {
    'variety': ['Manchuria', 'Manchuria', 'Manchuria', 'Glabron', 'Glabron', 'Glabron', 'Peatland', 'Peatland', 'Peatland', 'Svansota', 'Svansota', 'Svansota', 'Velvet', 'Velvet', 'Velvet', 'Trebi', 'Trebi', 'Trebi'],
    'site': ['Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm'],
    'yield': [27.00, 48.87, 28.70, 27.43, 50.31, 31.99, 27.66, 49.32, 29.47, 27.88, 51.49, 31.32, 28.12, 51.66, 30.35, 28.32, 52.08, 31.12]
}
source = pd.DataFrame(data)

variety_totals = source.groupby('variety')['yield'].sum()
source['proportion'] = source.apply(lambda row: row['yield'] / variety_totals[row['variety']], axis=1)

varieties = source['variety'].unique()
sites = source['site'].unique()

fig, ax = plt.subplots()

bottom = np.zeros(len(varieties))

for site in sites:
    site_data = source[source['site'] == site]
    site_proportions = site_data.groupby('variety')['proportion'].sum().reindex(varieties, fill_value=0)

    ax.barh(varieties, site_proportions, left=bottom)
    bottom += site_proportions

ax.legend()
plt.show()