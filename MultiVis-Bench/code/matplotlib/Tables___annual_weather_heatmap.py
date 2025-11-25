import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(0)
dates = pd.to_datetime(['2023-01-01'] + [pd.Timestamp('2023-01-01') + pd.Timedelta(days=i) for i in range(1, 365)])
temp_max = np.random.uniform(5, 25, size=365)

source = pd.DataFrame({'date': dates, 'temp_max': temp_max})
source['month'] = source['date'].dt.month_name()
source['day'] = source['date'].dt.day

heatmap_data = source.pivot_table(index='month', columns='day', values='temp_max')

month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
heatmap_data = heatmap_data.reindex(month_order)

fig, ax = plt.subplots()

im = ax.imshow(heatmap_data, cmap='viridis', aspect='auto')

days_labels = heatmap_data.columns.tolist()
month_labels = heatmap_data.index.tolist()

ax.set_xticks(np.arange(len(days_labels)))
ax.set_xticklabels(days_labels)
ax.set_yticks(np.arange(len(month_labels)))
ax.set_yticklabels(month_labels)

plt.show()