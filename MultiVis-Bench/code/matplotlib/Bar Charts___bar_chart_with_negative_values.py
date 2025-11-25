import matplotlib.pyplot as plt
import numpy as np

months = np.arange(1, 13)
np.random.seed(0)
nonfarm_change = (np.random.randn(12) * 100).astype(int)

colors = []
for change in nonfarm_change:
    if change > 0:
        colors.append('steelblue')
    else:
        colors.append('orange')

plt.bar(months, nonfarm_change, color=colors)
plt.xlabel("Month")
plt.xticks(months)
plt.ylabel("Nonfarm Change")
plt.axhline(0, color='black', linewidth=0.8, linestyle='--')

plt.show()