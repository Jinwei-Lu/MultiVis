import matplotlib.pyplot as plt
import pandas as pd
from vega_datasets import data
import numpy as np

source = data.iowa_electricity()
source_df = pd.DataFrame(source)

years = sorted(source_df['year'].unique())
sources = source_df['source'].unique()
source_generation = {}

for s in sources:
    source_data = source_df[source_df['source'] == s].set_index('year')
    source_generation[s] = source_data.reindex(years)['net_generation'].fillna(0).values

total_generation_per_year = np.sum(list(source_generation.values()), axis=0)

normalized_generation = {}
for s in sources:
    normalized_generation[s] = source_generation[s] / total_generation_per_year

fig, ax = plt.subplots()

y_stack = np.zeros(len(years))

for i, s in enumerate(sources):
    ax.fill_between(years, y_stack, y_stack + normalized_generation[s], label=s)
    y_stack += normalized_generation[s]

ax.set_xlabel('Year')
ax.set_ylabel('Normalized Net Generation')
ax.legend()
ax.set_xlim(min(years), max(years))
ax.set_ylim(0, 1)

plt.show()