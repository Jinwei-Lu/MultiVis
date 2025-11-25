import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

rng = np.random.RandomState(1)
x = rng.rand(40) ** 2
y = 10 - 1.0 / (x + 0.1) + rng.randn(40)

source = pd.DataFrame({"x": x, "y": y})

degree_list = [1, 3, 5]

fig, ax = plt.subplots()

ax.scatter(source["x"], source["y"])

for order in degree_list:
    coeffs = np.polyfit(source["x"], source["y"], order)
    x_fit = np.linspace(source["x"].min(), source["x"].max(), 100)
    y_fit = np.polyval(coeffs, x_fit)
    ax.plot(x_fit, y_fit)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()

plt.show()