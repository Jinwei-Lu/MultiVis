import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 5000
dates = pd.to_datetime('2024-01-01') + pd.to_timedelta(np.random.randint(0, 365, n_samples), unit='D')
times = pd.to_timedelta(np.random.randint(0, 24 * 60, n_samples), unit='m')
dates = dates + times
df = pd.DataFrame({'date': dates})
df['time'] = df['date'].dt.hour + df['date'].dt.minute / 60

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=False)

bins = np.linspace(0, 24, 31)
counts, edges = np.histogram(df['time'], bins=bins)
bin_centers = (edges[:-1] + edges[1:]) / 2

ax1.bar(bin_centers, counts, width=(bins[1]-bins[0]), align='center')
ax1.set_ylabel('Count')
ax1.set_xlim(0, 24)

ax2.bar(bin_centers, counts, width=(bins[1]-bins[0]), align='center')
ax2.set_ylabel('Count')
ax2.set_xlabel('Time (Hours)')
ax2.set_xlim(0, 24)

selection_start = None
selection_end = None
selection_rect = None

def on_press(event):
    global selection_start, selection_rect
    if event.inaxes == ax2:
        selection_start = event.xdata
        if selection_rect:
            selection_rect.remove()
        selection_rect = plt.Rectangle((selection_start, ax2.get_ylim()[0]), 0, ax2.get_ylim()[1] - ax2.get_ylim()[0],
                                        color='gray', alpha=0.3)
        ax2.add_patch(selection_rect)
        fig.canvas.draw_idle()

def on_motion(event):
    global selection_start, selection_end, selection_rect
    if event.inaxes == ax2 and selection_start is not None:
        selection_end = event.xdata
        width = selection_end - selection_start
        if selection_rect:
            selection_rect.set_width(width)
            selection_rect.set_x(min(selection_start, selection_end))
        fig.canvas.draw_idle()

def on_release(event):
    global selection_start, selection_end, selection_rect
    if event.inaxes == ax2 and selection_start is not None and selection_end is not None:
        selection_end = event.xdata
        xmin = min(selection_start, selection_end)
        xmax = max(selection_start, selection_end)
        if xmin != xmax:
            ax1.set_xlim(xmin, xmax)
            if selection_rect:
                selection_rect.remove()
                selection_rect = None
        selection_start = None
        selection_end = None
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

plt.show()