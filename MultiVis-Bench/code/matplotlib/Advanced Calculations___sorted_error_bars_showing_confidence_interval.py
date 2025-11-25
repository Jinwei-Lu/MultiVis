import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
varieties = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
n_varieties = len(varieties)
n_samples = 20

data = []
for variety in varieties:
    yield_mean = np.random.uniform(20, 40)
    yield_std = np.random.uniform(3, 8)
    yield_values = np.random.normal(yield_mean, yield_std, n_samples)
    for y in yield_values:
        data.append({'variety': variety, 'yield': y})

df = pd.DataFrame(data)

means = df.groupby('variety')['yield'].mean()
stds = df.groupby('variety')['yield'].std()
ci0 = means - 1.96 * stds / np.sqrt(n_samples)
ci1 = means + 1.96 * stds / np.sqrt(n_samples)

sorted_varieties = means.sort_values(ascending=False).index
means_sorted = means[sorted_varieties]
ci0_sorted = ci0[sorted_varieties]
ci1_sorted = ci1[sorted_varieties]

fig, ax = plt.subplots()

ax.scatter(means_sorted, sorted_varieties, color='black', marker='o')

for i, variety in enumerate(sorted_varieties):
    ax.plot([ci0_sorted[i], ci1_sorted[i]], [variety, variety], color='black')

ax.set_xlabel('Barley Yield')
ax.set_ylabel('Variety')

plt.show()