import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)
x = [1, 2, 3, 4, 5]
y = np.random.normal(10, 0.5, size=len(x))
yerr = 0.2

fig, ax = plt.subplots()

ax.errorbar(x, y, yerr=yerr, fmt='none', ecolor='black', capsize=4)
ax.plot(x, y, 'o', color='black')

ax.set_xlim(0, 6)
ax.set_ylim(min(y - yerr) - 0.2, max(y + yerr) + 0.2)
ax.set_xlabel("x")
ax.set_ylabel("y")

plt.show()