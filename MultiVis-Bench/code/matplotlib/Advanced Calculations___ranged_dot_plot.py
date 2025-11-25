import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = {
    'country': ['China', 'India', 'United States', 'Indonesia', 'Brazil'] * 2,
    'year': [1955] * 5 + [2000] * 5,
    'life_expect': np.random.rand(10) * 30 + 50
}
df = pd.DataFrame(data)

fig, ax = plt.subplots()

for country in df['country'].unique():
    subset = df[df['country'] == country]
    ax.plot(subset['life_expect'], [country] * len(subset))

for year in df['year'].unique():
    subset = df[df['year'] == year]
    ax.scatter(subset['life_expect'], subset['country'])

ax.set_xlabel('Life Expectancy')
ax.set_ylabel('Country')
ax.legend()

plt.show()