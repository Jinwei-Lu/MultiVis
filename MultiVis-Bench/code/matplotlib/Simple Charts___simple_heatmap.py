import matplotlib.pyplot as plt
import numpy as np

x, y = np.meshgrid(range(-5, 5), range(-5, 5))
z = x ** 2 + y ** 2

plt.imshow(z, extent=[-5, 5, -5, 5], origin='lower', cmap='viridis')
plt.colorbar()
plt.show()