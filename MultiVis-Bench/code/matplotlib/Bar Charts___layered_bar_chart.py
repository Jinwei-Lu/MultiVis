import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

years = np.arange(2010, 2021)
sources = ['Coal', 'Nuclear', 'Natural Gas']
data = []
for year in years:
    for source in sources:
        data.append({'year': year, 'source': source, 'net_generation': np.random.randint(500, 2000)})
df = pd.DataFrame(data)
df_pivot = df.pivot(index='year', columns='source', values='net_generation').fillna(0)

fig, ax = plt.subplots()

width = 0.8
bottom = np.zeros(len(years))

for i, source in enumerate(sources):
    ax.bar(df_pivot.index, df_pivot[source], width, label=source, bottom=bottom)
    bottom += df_pivot[source].values

ax.set_xlabel('Year')
ax.set_ylabel('Net Generation')
ax.legend()
ax.set_xticks(years)
plt.xticks(rotation=45)
plt.show()