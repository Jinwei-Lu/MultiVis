import matplotlib.pyplot as plt
import pandas as pd

data = {'site': ['Site A', 'Site B', 'Site C', 'Site D', 'Site E'],
        'yield': [50, 80, 60, 90, 70],
        'variety': ['Variety1', 'Variety2', 'Variety3', 'Variety4', 'Variety5'],
        'year': [1930, 1931, 1932, 1933, 1934]}
source = pd.DataFrame(data)

site_yield = source.groupby('site')['yield'].sum().reset_index()
site_yield_sorted = site_yield.sort_values(by='yield', ascending=False)

plt.barh(site_yield_sorted['site'], site_yield_sorted['yield'])
plt.gca().invert_yaxis()
plt.show()