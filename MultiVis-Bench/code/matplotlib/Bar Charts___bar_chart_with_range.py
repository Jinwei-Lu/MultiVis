import matplotlib.pyplot as plt

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
temp_min = [-2, 0, 3, 7, 11, 14, 16, 16, 13, 8, 3, 0]
temp_max = [8, 10, 13, 17, 21, 24, 26, 26, 23, 18, 12, 9]

fig, ax = plt.subplots()

for i, month in enumerate(months):
    ax.barh(y=i, width=temp_max[i] - temp_min[i], left=temp_min[i])

for i, month in enumerate(months):
    ax.text(x=temp_min[i], y=i, s=str(temp_min[i]), ha='right', va='center')

for i, month in enumerate(months):
    ax.text(x=temp_max[i], y=i, s=str(temp_max[i]), ha='left', va='center')

ax.set_xlim([-15, 45])
ax.set_yticks(range(len(months)))
ax.set_yticklabels(months)

ax.invert_yaxis()

plt.show()