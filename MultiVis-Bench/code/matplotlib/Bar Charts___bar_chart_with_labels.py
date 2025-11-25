import matplotlib.pyplot as plt
import numpy as np

years = np.arange(1565, 1825, 5)
wheat_values = np.array([41, 45, 42, 49, 41.5, 47, 64, 27, 33, 32, 33, 35, 33, 45, 33, 39, 53, 42, 40.5, 46.5, 32, 37, 43, 35, 27, 40, 50, 30, 32, 44, 33, 29, 39, 26, 32, 27, 27.5, 31, 35.5, 31, 43, 47, 44, 46, 42, 47.5, 76, 79, 81, 99, 78, 54])
wheat_values = wheat_values[:len(years)]

fig, ax = plt.subplots()

bars = ax.barh(years.astype(str), wheat_values)

for bar in bars:
    width = bar.get_width()
    label_x_pos = width + 2
    ax.text(label_x_pos, bar.get_y() + bar.get_height()/2,
            f'{width:.0f}' if width == int(width) else f'{width:.1f}',
            va='center', ha='left')

ax.set_xlabel("wheat")
ax.set_ylabel("year")
ax.invert_yaxis()

plt.show()