import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

medians = pd.DataFrame(
    [
        {"name": "Identify Errors:", "median": 2.0, "lo": "Easy", "hi": "Hard"},
        {"name": "Fix Errors:", "median": 2.1, "lo": "Easy", "hi": "Hard"},
        {"name": "Easier to Fix:", "median": 2.0, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Faster to Fix:", "median": 2.6, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Easier on Phone:", "median": 1.6, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Easier on Tablet:", "median": 3.1, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Device Preference:", "median": 4.6, "lo": "Phone", "hi": "Tablet"},
    ]
)

values_data = []
for name in medians['name']:
    for value in range(1, 6):
        count = np.random.randint(0, 10)
        values_data.append({'name': name, 'value': value, 'count': count})
values = pd.DataFrame(values_data)

fig, ax = plt.subplots()

for name in medians['name']:
    subset = values[values['name'] == name]
    ax.scatter(subset['value'], [name] * len(subset), s=subset['count'] * 20)

for i, row in medians.iterrows():
    ax.plot([row['median'], row['median']], [i - 0.3, i + 0.3], color='black')

y_positions = range(len(medians))

for i, row in medians.iterrows():
    ax.text(-0.3, i, row['lo'], ha='right', va='center')
    ax.text(5.3, i, row['hi'], ha='left', va='center')

ax.set_xlim(0, 6)
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_yticks(y_positions)
ax.set_yticklabels(medians['name'])

plt.show()