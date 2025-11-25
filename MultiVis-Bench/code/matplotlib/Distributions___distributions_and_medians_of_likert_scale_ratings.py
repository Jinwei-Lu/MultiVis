import matplotlib.pyplot as plt
import pandas as pd

medians = pd.DataFrame(
    [
        {"name": "Identify Errors:", "median": 2.0, "lo": "Easy", "hi": "Hard"},
        {"name": "Fix Errors:", "median": 2.5, "lo": "Easy", "hi": "Hard"},
        {"name": "Easier to Fix:", "median": 2.0, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Faster to Fix:", "median": 3.0, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Easier on Phone:", "median": 1.8, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Easier on Tablet:", "median": 3.2, "lo": "Toolbar", "hi": "Gesture"},
        {"name": "Device Preference:", "median": 4.0, "lo": "Phone", "hi": "Tablet"},
    ]
)

values_data = {
    "Identify Errors:": [2, 2, 2, 3, 2, 1, 2, 3, 2, 2, 2, 1, 2, 3, 4, 1, 3],
    "Fix Errors:": [2, 3, 2, 3, 2, 3, 3, 1, 3, 2, 2, 3, 2, 3, 5, 3, 2],
    "Easier to Fix:": [3, 4, 2, 2, 4, 3, 4, 2, 2, 1, 1, 2, 1, 2, 1, 2, 2],
    "Faster to Fix:": [4, 5, 1, 2, 4, 4, 5, 4, 4, 1, 1, 3, 1, 2, 1, 2, 2],
    "Easier on Phone:": [2, 5, 2, 4, 4, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "Easier on Tablet:": [5, 5, 1, 1, 5, 4, 2, 5, 4, 1, 1, 3, 1, 1, 1, 4, 3],
    "Device Preference:": [5, 5, 5, 5, 5, 4, 4, 5, 4, 5, 4, 3, 5, 1, 5, 5, 2],
}

values = []
for name, vals in values_data.items():
    for v in vals:
        values.append({"name": name, "value": v})
values = pd.DataFrame(values)

fig, ax = plt.subplots()

for name in medians["name"]:
    subset = values[values["name"] == name]
    value_counts = subset["value"].value_counts().sort_index()
    x_vals = value_counts.index
    y_vals = [name] * len(x_vals)
    sizes = value_counts.values * 20
    ax.scatter(x_vals, y_vals, s=sizes, color="#6EB4FD")

for i, row in medians.iterrows():
    ax.plot([row["median"], row["median"]], [i - 0.3, i + 0.3], color="black")

for i, row in medians.iterrows():
    ax.text(-0.5, i, row["lo"], ha="right", va="center")
    ax.text(5.5, i, row["hi"], ha="left", va="center")

ax.set_xlim(0, 6)
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_yticks(range(len(medians)))
ax.set_yticklabels(medians["name"])

plt.show()