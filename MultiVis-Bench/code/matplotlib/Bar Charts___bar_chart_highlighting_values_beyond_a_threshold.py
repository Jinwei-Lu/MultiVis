import matplotlib.pyplot as plt
import numpy as np

days = np.arange(1, 16)
values = np.random.randint(20, 180, size=15)
values[8] = 395
threshold = 300

fig, ax = plt.subplots()

ax.bar(days, values)
above_threshold_indices = np.where(values > threshold)[0]
ax.bar(days[above_threshold_indices], values[above_threshold_indices])

for i in above_threshold_indices:
    ax.bar(days[i], threshold)

ax.axhline(y=threshold)

ax.set_xlabel("Day")
ax.set_ylabel("Value")

ax.set_xticks(days)
ax.set_xticklabels(days, rotation=90)

ax.set_ylim(0, 400)

plt.show()