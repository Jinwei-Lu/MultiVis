import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
years = np.arange(1810, 1911, 10)
wheat_production = np.random.randint(20, 60, size=len(years)) + np.sin(np.linspace(0, 10, len(years))) * 20
data = pd.DataFrame({'year': years, 'wheat': wheat_production})

data['rolling_mean'] = data['wheat'].rolling(window=10, min_periods=1).mean()

fig, ax = plt.subplots()

ax.bar(data['year'], data['wheat'], label='Wheat Production')

ax.plot(data['year'], data['rolling_mean'], label='10-year Rolling Mean')

ax.set_xlabel('Year')
ax.set_ylabel('Wheat Production')

ax.set_xticks(years)

ax.legend()

plt.show()