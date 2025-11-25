import matplotlib.pyplot as plt
import numpy as np

x = np.arange(1, 21)
y = np.random.randint(10, 100, size=20)
ny = y - 50

fig, axes = plt.subplots(2, 1, sharex=True)

axes[0].plot(x, y)
axes[0].fill_between(x, y, 50)
axes[0].set_ylim(0, 50)
axes[0].set_ylabel('y')
axes[0].set_xlim(x.min(), x.max())

axes[1].plot(x, ny)
axes[1].fill_between(x, ny, -50)
axes[1].set_ylim(0, -50)
axes[1].invert_yaxis()
axes[1].set_ylabel('ny')
axes[1].set_xlabel('x')
axes[1].set_xlim(x.min(), x.max())

fig.subplots_adjust(hspace=0)
plt.show()