import matplotlib.pyplot as plt
import numpy as np

hours = np.arange(24)
observations = np.array([2, 2, 2, 2, 2, 3, 4, 4, 8, 8, 9, 7, 5, 6, 8, 8, 7, 7, 4, 3, 3, 2, 2, 2])

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

theta = np.linspace(0, 2 * np.pi, len(hours), endpoint=False)
width = (2 * np.pi) / len(hours)
radii = observations
ax.bar(theta, radii, width=width, bottom=1)

for radius in range(2, 11, 2):
    ax.plot(np.linspace(0, 2 * np.pi, 100), [radius] * 100)

for radius in range(2, 11, 2):
    ax.text(np.pi / 4, radius + 0.25, str(radius))

hour_labels = ['00:00', '06:00', '12:00', '18:00']
hour_thetas = [0, np.pi / 2, np.pi, 3 * np.pi / 2]
for hour_theta in hour_thetas:
    ax.plot([hour_theta, hour_theta], [1, 10])

for i, hour_theta in enumerate(hour_thetas):
    label = hour_labels[i]
    ha = 'center'
    va = 'center'
    angle_deg = np.degrees(hour_theta)
    if angle_deg == 270:
        ha = "right"
    if angle_deg == 90:
        ha = "left"
    if angle_deg == 0:
        va = "bottom"
    elif angle_deg == 180:
        va = "top"
    ax.text(hour_theta - np.pi/16, 10 + 0.5, label, ha=ha, va=va)

ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.spines['polar'].set_visible(False)
ax.grid(False)
ax.set_ylim(0, 11)

plt.show()