import matplotlib.pyplot as plt
import numpy as np

x = np.arange(0, 12.7, 0.1)
sin_y = np.sin(x)
cos_y = np.cos(x)

fig, ax = plt.subplots()
ax.plot(x, sin_y, label='sin')
ax.plot(x, cos_y, label='cos')

ax.set_xlabel('x')
ax.set_ylabel('value')

ax.legend()

plt.show()