import matplotlib.pyplot as plt
import numpy as np

sites = ['Waseca', 'Crookston', 'Morris', 'University Farm', 'Duluth', 'Grand Rapids']
yields = np.array([962, 748, 708, 653, 560, 499])

fig, ax = plt.subplots()

cmap = plt.get_cmap('Blues')
norm = plt.Normalize(yields.min(), yields.max())

for i, (site, yield_val) in enumerate(zip(sites, yields)):
    color = cmap(norm(yield_val))
    ax.barh(site, yield_val, color=color)

for i, yield_val in enumerate(yields):
    bar_color = cmap(norm(yield_val))
    luminance = 0.299 * bar_color[0] + 0.587 * bar_color[1] + 0.114 * bar_color[2]
    text_color = 'black' if luminance > 0.5 else 'white'
    ax.text(yield_val - 3, i, f'{yield_val:.0f}', ha='right', va='center', color=text_color)

ax.set_xlabel('Sum of yield')
ax.set_ylabel('site')
ax.set_xticks(np.arange(0, 1001, 200))
ax.set_xlim(0, 1100)
ax.invert_yaxis()

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label('Sum of yield')
cbar.set_ticks([yields.min(), yields.max()])

plt.show()