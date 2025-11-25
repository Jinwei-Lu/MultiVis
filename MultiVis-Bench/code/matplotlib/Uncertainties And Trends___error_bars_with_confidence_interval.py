import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
varieties = ['A', 'B', 'C', 'D', 'E']
years = [2020, 2021, 2022]
sites = ['Site1', 'Site2', 'Site3']

data = []
for variety in varieties:
    for year in years:
        for site in sites:
            yield_val = np.random.normal(loc=30 + (ord(variety) - ord('A')) * 5, scale=10)
            data.append([variety, year, site, yield_val])

source = pd.DataFrame(data, columns=['variety', 'year', 'site', 'yield'])

means = source.groupby('variety')['yield'].mean()
ci = 1.96 * source.groupby('variety')['yield'].std() / np.sqrt(source.groupby('variety')['yield'].count())

fig, ax = plt.subplots()

for i, variety in enumerate(varieties):
    ax.errorbar(
        means[variety],
        i,
        xerr=ci[variety],
        fmt='none',
    )

ax.scatter(
    means,
    range(len(varieties)),
)

ax.set_yticks(range(len(varieties)))
ax.set_yticklabels(varieties)
ax.set_xlim(0, None)

plt.show()