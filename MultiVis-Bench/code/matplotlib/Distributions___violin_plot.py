import matplotlib.pyplot as plt
import numpy as np

europe_mpg = np.concatenate([
    np.random.normal(28, 5, 150),
    np.random.normal(40, 3, 50),
    np.random.normal(18, 3, 30)
])
japan_mpg = np.concatenate([
    np.random.normal(32, 6, 180),
    np.random.normal(45, 4, 70),
    np.random.normal(25, 2, 20)
])
usa_mpg = np.concatenate([
    np.random.normal(22, 4, 200),
    np.random.normal(15, 3, 50),
    np.random.normal(35, 2, 10)
])

data = [europe_mpg, japan_mpg, usa_mpg]
labels = ['Europe', 'Japan', 'USA']

fig, ax = plt.subplots()

parts = ax.violinplot(data, positions=range(len(labels)), vert=True, widths=0.7,
                      showmeans=False, showextrema=False, showmedians=False)

for i, pc in enumerate(parts['bodies']):
    pc.set_edgecolor('black')

ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels)
ax.set_ylabel('Miles per_Gallon')
ax.set_xlabel('Origin')
ax.set_xlim(-0.5, len(labels) - 0.5)
ax.set_ylim(5, 50)

plt.show()