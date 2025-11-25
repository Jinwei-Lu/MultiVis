import matplotlib.pyplot as plt
import pandas as pd

source = pd.DataFrame([
    {"task": "A", "start": 1, "end": 3},
    {"task": "B", "start": 3, "end": 8},
    {"task": "C", "start": 8, "end": 10}
])

fig, ax = plt.subplots()

for index, row in source.iterrows():
    ax.barh(row['task'], row['end'] - row['start'], left=row['start'])

ax.invert_yaxis()

plt.show()