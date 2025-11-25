import matplotlib.pyplot as plt
import numpy as np

age_groups = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
data_for_boxplot = []

for _ in age_groups:
    data = np.random.normal(loc=5000, scale=2000, size=100)
    data = np.clip(data, 0, 15000)
    data_for_boxplot.append(data)

plt.boxplot(data_for_boxplot, labels=age_groups, showfliers=False)
plt.xlabel('age')
plt.ylabel('people')

plt.show()