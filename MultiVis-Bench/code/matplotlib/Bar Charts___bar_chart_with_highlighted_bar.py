import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

years = np.arange(1790, 1880, 10)
wheat = np.random.randint(20, 80, size=len(years))
source = pd.DataFrame({'year': years, 'wheat': wheat})

for i in range(len(source)):
    if source['year'][i] == 1810:
        color = 'orange'
    else:
        color = 'steelblue'
    plt.bar(source['year'][i], source['wheat'][i], color=color)

plt.xlabel("Year")
plt.ylabel("Wheat Production")
plt.xticks(years)
plt.show()