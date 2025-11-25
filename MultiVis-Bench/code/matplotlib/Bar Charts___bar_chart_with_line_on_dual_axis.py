import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

years = np.arange(1810, 1940, 10)
wheat = np.random.randint(20, 80, size=len(years))
wages = np.random.randint(5, 40, size=len(years)) + 0.5 * np.arange(len(years))

data = pd.DataFrame({'year': years, 'wheat': wheat, 'wages': wages})

fig, ax = plt.subplots()

ax.bar(data['year'], data['wheat'], label='wheat', width=5)
ax.plot(data['year'], data['wages'], label='wages')

ax.set_xticks(years)

ax.legend()

plt.show()