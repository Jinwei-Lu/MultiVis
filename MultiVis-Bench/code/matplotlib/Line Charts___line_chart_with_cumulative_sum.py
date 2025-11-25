import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
years = np.arange(1810, 1940, 10)
wheat_production = np.random.randint(10, 100, size=len(years))

data = pd.DataFrame({'year': years, 'wheat': wheat_production})
data['cumulative_wheat'] = data['wheat'].cumsum()

plt.plot(data['year'], data['cumulative_wheat'], marker='o', linestyle='-')
plt.xlabel('Year')
plt.ylabel('Cumulative Wheat Production')
plt.xticks(years)
plt.show()