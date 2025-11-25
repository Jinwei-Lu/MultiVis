import matplotlib.pyplot as plt
import numpy as np

x = np.arange(0, 100)
y = np.sin(x / 5)

fig, ax = plt.subplots()
ax.plot(x, y)

plt.show()