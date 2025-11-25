import matplotlib.pyplot as plt
import numpy as np

miles = np.array([3800, 3900, 4000, 4100, 4200, 4300, 4500, 4700, 4900, 5100,
                  5300, 5500, 5700, 5900, 6000, 6100, 6300, 6500, 6700, 6800,
                  6900, 7000, 7100, 7200, 7300, 7500, 7600, 7800, 8000, 8200,
                  8400, 8500, 8600, 8800, 8900, 9000, 9200, 9300, 9400, 9500,
                  9600, 9700, 9800, 9900, 9950, 10000, 10050, 10100])

gas = np.array([2.4, 2.3, 2.25, 2.2, 2.1, 2.1, 2.12, 2.12, 2.12, 2.08,
                2.03, 1.98, 1.9, 1.87, 1.84, 2.32, 2.3, 2.32, 2.35, 3.3,
                2.9, 2.7, 2.5, 2.4, 2.3, 1.7, 1.7, 1.7, 1.6, 1.65,
                1.75, 1.8, 1.9, 1.6, 1.55, 1.5, 1.6, 1.58, 1.58, 1.5,
                1.3, 1.4, 1.6, 1.9, 3.4, 3.2, 2.9, 2.4])

year = np.arange(len(miles))

sorted_indices = np.argsort(year)
miles = miles[sorted_indices]
gas = gas[sorted_indices]

fig, ax = plt.subplots()

ax.plot(miles, gas, marker='o', linestyle='-')

ax.set_xlim(miles.min(), miles.max())
ax.set_ylim(gas.min(), gas.max())

ax.set_xlabel("miles")
ax.set_ylabel("gas")

plt.show()