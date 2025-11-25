import matplotlib.pyplot as plt

project = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
score = [25, 57, 23, 19, 8, 47, 8]
goal = [25, 47, 30, 27, 38, 19, 4]

bar_width = 0.8
tick_width = 2
tick_size_factor = 0.9 * bar_width

fig, ax = plt.subplots()

ax.bar(project, score, width=bar_width)

for i, (proj, g) in enumerate(zip(project, goal)):
    ax.plot([i - tick_size_factor / 2, i + tick_size_factor / 2], [g, g],
            linewidth=tick_width, solid_capstyle='butt')

ax.set_xticks(range(len(project)))
ax.set_xticklabels(project)

plt.show()