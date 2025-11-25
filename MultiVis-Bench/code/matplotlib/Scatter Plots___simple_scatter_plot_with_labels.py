import matplotlib.pyplot as plt
import pandas as pd

source = pd.DataFrame({
    'x': [1, 3, 5, 7, 9],
    'y': [2, 4, 1, 8, 6],
    'label': ['A', 'B', 'C', 'D', 'E']
})

fig, ax = plt.subplots()
ax.scatter(source['x'], source['y'], marker='o')

for i in range(len(source)):
    ax.text(source['x'][i] + 0.7, source['y'][i], source['label'][i])

plt.show()