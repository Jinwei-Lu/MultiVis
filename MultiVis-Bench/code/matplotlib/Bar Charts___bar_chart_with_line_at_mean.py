import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

years = np.arange(1810, 1940, 10)
wheat_production = np.random.randint(20, 80, size=len(years))

source = pd.DataFrame({'year': years, 'wheat': wheat_production})

plt.bar(source['year'], source['wheat'], width=5)

mean_wheat = source['wheat'].mean()

plt.axhline(y=mean_wheat, color='red', linestyle='-', linewidth=2)

plt.xticks(years)

plt.show()