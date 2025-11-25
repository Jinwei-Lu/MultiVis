import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)
horsepower_data = np.concatenate([
    np.random.normal(80, 20, 300),
    np.random.normal(120, 30, 200),
    np.random.normal(160, 40, 100),
    np.random.normal(200, 50, 50),
    np.random.normal(40, 10, 20),
    np.random.normal(240, 60, 10)
])
horsepower_data = horsepower_data[(horsepower_data > 0) & (horsepower_data < 300)]

bins = np.arange(20, 260, 20)
counts, bin_edges = np.histogram(horsepower_data, bins=bins)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

fig, ax = plt.subplots()

bar_width = 18
for i in range(len(counts)):
    ax.bar(bin_centers[i], counts[i], width=bar_width, bottom=-counts[i]/2, align='center')

inner_bar_width = 18
for i in range(len(counts)):
    ax.bar(bin_centers[i], counts[i], width=inner_bar_width, bottom=-counts[i]/2, align='center')

ax.set_xticks(bins)
ax.set_xlim(0, 260)

plt.show()