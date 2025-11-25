import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.DataFrame({
    "x": np.random.uniform(-4, 5, size=50),
    "y": np.random.uniform(2, 5, size=50),
})

df = pd.DataFrame({
    "x": range(7),
    "ymin": range(7),
    "ymax": range(1, 8)
})

rect_data = pd.DataFrame({
    "x1": [-2],
    "x2": [-1]
})

fig, ax = plt.subplots()

ax.scatter(data["x"], data["y"], marker='o')

ax.fill_between(df["x"], df["ymin"], df["ymax"], alpha=0.3)

rect_x = rect_data["x1"][0]
rect_width = rect_data["x2"][0] - rect_data["x1"][0]
rect = plt.Rectangle((rect_x, 0), rect_width, ax.get_ylim()[1], color='red', alpha=0.3)
ax.add_patch(rect)

plt.show()