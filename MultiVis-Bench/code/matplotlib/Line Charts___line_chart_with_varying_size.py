import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
years = np.arange(1800, 1900)
wheat = 40 + np.random.randn(100) * 5 + np.sin(np.linspace(0, 10, 100)) * 10
wheat[80:90] = wheat[80:90] + np.arange(10) * 5
wheat = np.clip(wheat, 0, 100)

data = pd.DataFrame({'year': years, 'wheat': wheat})

normalized_wheat = (data['wheat'] - data['wheat'].min()) / (data['wheat'].max() - data['wheat'].min())
sizes = 5 + normalized_wheat * 40

for i in range(len(data) - 1):
    plt.plot(
        [data['year'][i], data['year'][i+1]],
        [data['wheat'][i], data['wheat'][i+1]],
        linewidth=sizes[i]/5,
    )

plt.xlabel("year")
plt.ylabel("wheat")

plt.xlim(data['year'].min() - 2, data['year'].max() + 2)
plt.ylim(0, 100)

plt.show()