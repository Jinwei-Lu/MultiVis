import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

years = range(1990, 2001)
wheat_values = np.random.randint(30, 100, size=len(years))

source = pd.DataFrame({'year': years, 'wheat': wheat_values})

fig, ax = plt.subplots()
ax.barh(source['year'].astype(str), source['wheat'])
ax.set_ylabel('year')
ax.set_xlabel('wheat')
ax.invert_yaxis()

plt.show()