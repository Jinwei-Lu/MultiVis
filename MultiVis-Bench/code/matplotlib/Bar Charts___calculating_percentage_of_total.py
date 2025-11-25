import matplotlib.pyplot as plt
import pandas as pd

source = pd.DataFrame({
    'Activity': ['Sleeping', 'Eating', 'TV', 'Work', 'Exercise'],
    'Time': [8, 2, 4, 8, 2]
})

total_time = source['Time'].sum()
source['PercentOfTotal'] = source['Time'] / total_time

fig, ax = plt.subplots()
ax.barh(source['Activity'], source['PercentOfTotal'])
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: '{:.0%}'.format(x)))

plt.show()