import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

np.random.seed(42)
data = np.random.normal(loc=6.5, scale=1.5, size=3000)
data = data[(data > 1) & (data < 10)]

bins = np.linspace(1, 10, 21)
counts, _ = np.histogram(data, bins=bins)

fig, ax = plt.subplots()

cmap = cm.get_cmap('PiYG')
norm = plt.Normalize(bins.min(), bins.max())

for i in range(len(counts)):
    color = cmap(norm(bins[i]))
    ax.bar(bins[i] + (bins[1] - bins[0]) / 2, counts[i], width=(bins[1] - bins[0]), color=color, edgecolor='white')

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
tick_positions = np.linspace(1, 10, 10)
cbar.set_ticks(tick_positions)
cbar_tick_labels = [str(round(x, 1)) for x in tick_positions]
cbar.set_ticklabels(cbar_tick_labels)

plt.show()