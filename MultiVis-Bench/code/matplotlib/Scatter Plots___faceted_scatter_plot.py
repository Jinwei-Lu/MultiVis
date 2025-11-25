import matplotlib.pyplot as plt
import numpy as np

origins = ['USA'] * 50 + ['Europe'] * 30 + ['Japan'] * 40
horsepower = np.concatenate([
    np.random.normal(150, 30, 50),
    np.random.normal(100, 20, 30),
    np.random.normal(80, 15, 40)
])
mpg = np.concatenate([
    np.random.normal(25, 5, 50) - horsepower[:50] / 30,
    np.random.normal(30, 6, 30) - horsepower[50:80] / 30,
    np.random.normal(35, 7, 40) - horsepower[80:] / 30
])

mpg = np.clip(mpg, 5, 50)
horsepower = np.clip(horsepower, 50, 300)

unique_origins = sorted(list(set(origins)))
num_origins = len(unique_origins)

fig, axes = plt.subplots(num_origins, 1, sharex=True, sharey=True)

for i, origin in enumerate(unique_origins):
    ax = axes[i]
    origin_indices = [j for j, o in enumerate(origins) if o == origin]
    ax.scatter(horsepower[origin_indices], mpg[origin_indices])

    ax.set_ylabel('Miles_per_Gallon')

axes[-1].set_xlabel('Horsepower')
plt.show()