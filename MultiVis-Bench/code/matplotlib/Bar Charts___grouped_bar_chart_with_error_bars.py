import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

years = ['1931', '1932'] * 6
sites = ['Grand Rapids', 'Duluth', 'University Farm', 'Morris', 'Crookston', 'Waseca'] * 2
np.random.seed(42)

yields = []
for site in ['Grand Rapids', 'Duluth', 'University Farm', 'Morris', 'Crookston', 'Waseca']:
    yields.extend(np.random.normal(loc=30, scale=5, size=1) + np.random.randint(-5,6,size=1))
    yields.extend(np.random.normal(loc=35, scale=7, size=1) + np.random.randint(-5, 6, size=1))

df = pd.DataFrame({'year': years, 'site': sites, 'yield': yields})
df['year'] = df['year'].astype('category')

df_agg = df.groupby(['site', 'year'])['yield'].agg(['mean', 'std']).reset_index()

fig, axes = plt.subplots(1, 6, sharey=True)

for i, site in enumerate(df_agg['site'].unique()):
    ax = axes[i]
    site_data = df_agg[df_agg['site'] == site]

    ax.bar(
        site_data['year'],
        site_data['mean'],
        width=0.5
    )

    ax.errorbar(
        site_data['year'],
        site_data['mean'],
        yerr=site_data['std'],
        fmt='none',
        ecolor='black',
        capsize=5,
        capthick=1,
        elinewidth=1,
    )

axes[0].set_ylabel('Mean Yield')

plt.show()