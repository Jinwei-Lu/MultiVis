import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

source = pd.DataFrame({
    "Category":list("AAABBBCCC"),
    "Group":list("xyzxyzxyz"),
    "Value":[0.1, 0.6, 0.9, 0.7, 0.2, 1.1, 0.6, 0.1, 0.2]
})

categories = source['Category'].unique()
groups = source['Group'].unique()

bar_width = 0.2
x = np.arange(len(categories))
num_groups = len(groups)
group_offsets = np.linspace(-(bar_width * (num_groups - 1)) / 2, (bar_width * (num_groups - 1)) / 2, num_groups)

fig, ax = plt.subplots()

for i, group in enumerate(groups):
    group_data = source[source['Group'] == group]
    values = []
    for category in categories:
        val = group_data[group_data['Category'] == category]['Value'].values
        if len(val) > 0:
            values.append(val[0])
        else:
            values.append(0)
    ax.bar(x + group_offsets[i], values, bar_width, label=group)

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
plt.show()