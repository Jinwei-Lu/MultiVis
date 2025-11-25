import matplotlib.pyplot as plt
import numpy as np

varieties = ['Manchuria', 'Glabron', 'No. 475', 'Velvet', 'Trebi', 'Peatland']
mean_yields = [25, 28, 22, 30, 26, 24]
std_devs = [3, 4, 2, 5, 3.5, 2.5]

y_positions = np.arange(len(varieties))

plt.errorbar(mean_yields, y_positions, xerr=std_devs, fmt='none', ecolor='black', capsize=5, linewidth=1)
plt.scatter(mean_yields, y_positions, color='black', marker='o', facecolors='black')

plt.yticks(y_positions, varieties)
plt.xlim(left=0)

plt.gca().invert_yaxis()

plt.show()