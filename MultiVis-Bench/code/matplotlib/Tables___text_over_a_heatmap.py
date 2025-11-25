import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = {
    'Origin': ['USA', 'Europe', 'Japan', 'USA', 'Europe', 'Japan', 'USA', 'Europe', 'Japan'],
    'Cylinders': [4, 4, 4, 6, 6, 6, 8, 8, 8],
    'mean_horsepower': [80, 75, 70, 110, 105, 100, 180, 170, 160]
}
source = pd.DataFrame(data)

source['Origin'] = pd.Categorical(source['Origin'], categories=['USA', 'Europe', 'Japan'], ordered=True)
source['Cylinders'] = pd.Categorical(source['Cylinders'], categories=[4, 6, 8], ordered=True)

origins = source['Origin'].cat.categories.tolist()
cylinders = source['Cylinders'].cat.categories.tolist()

heatmap_data = source.pivot_table(index='Origin', columns='Cylinders', values='mean_horsepower')

fig, ax = plt.subplots()
im = ax.imshow(heatmap_data, cmap='viridis', aspect='auto')

cbar = ax.figure.colorbar(im, ax=ax)

ax.set_xticks(np.arange(len(cylinders)))
ax.set_yticks(np.arange(len(origins)))

ax.set_xticklabels(cylinders)
ax.set_yticklabels(origins)

for i in range(len(origins)):
    for j in range(len(cylinders)):
        mean_hp = heatmap_data.iloc[i, j]
        if not np.isnan(mean_hp):
            text = ax.text(j, i, f"{mean_hp:.0f}", ha="center", va="center")

ax.set_xlabel("Cylinders")
ax.set_ylabel("Origin")

plt.show()