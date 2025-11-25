import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 150
species = np.repeat(['setosa', 'versicolor', 'virginica'], n_samples / 3)
sepal_length = np.concatenate([
    np.random.normal(5.0, 0.35, int(n_samples / 3)),
    np.random.normal(5.9, 0.5, int(n_samples / 3)),
    np.random.normal(6.5, 0.6, int(n_samples / 3)),
])
sepal_width = np.concatenate([
    np.random.normal(3.4, 0.4, int(n_samples / 3)),
    np.random.normal(2.7, 0.3, int(n_samples / 3)),
    np.random.normal(3.0, 0.4, int(n_samples / 3)),
])

df = pd.DataFrame({'sepalLength': sepal_length, 'sepalWidth': sepal_width, 'species': species})

fig = plt.figure()
ax_main = plt.subplot(2, 2, 3)
ax_top = plt.subplot(2, 2, 1, sharex=ax_main)
ax_right = plt.subplot(2, 2, 4, sharey=ax_main)

for species_name, group in df.groupby('species'):
    ax_main.scatter(group['sepalLength'], group['sepalWidth'])

bins_top = np.linspace(4.0, 8.0, 21)
for species_name, group in df.groupby('species'):
    hist, _ = np.histogram(group['sepalLength'], bins=bins_top)
    ax_top.bar(bins_top[:-1], hist, width=(bins_top[1] - bins_top[0]), align='edge')

bins_right = np.linspace(1.9, 4.55, 21)
for species_name, group in df.groupby('species'):
    hist, _ = np.histogram(group['sepalWidth'], bins=bins_right)
    ax_right.barh(bins_right[:-1], hist, height=(bins_right[1] - bins_right[0]), align='edge')

ax_main.set_xlim(4.0, 8.0)
ax_main.set_ylim(1.9, 4.55)
ax_main.set_xlabel('sepalLength')
ax_main.set_ylabel('sepalWidth')

ax_top.tick_params(axis='both', which='both', labelbottom=False, labelleft=False, bottom=False, left=False)
ax_right.tick_params(axis='both', which='both', labelbottom=False, labelleft=False, bottom=False, left=False)

plt.show()