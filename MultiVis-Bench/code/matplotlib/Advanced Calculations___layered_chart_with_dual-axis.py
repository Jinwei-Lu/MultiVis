import matplotlib.pyplot as plt
import pandas as pd
from vega_datasets import data

source = data.seattle_weather()
df = pd.DataFrame(source)

df['date'] = pd.to_datetime(df['date'])

monthly_data = df.groupby(df['date'].dt.month).agg({
    'temp_max': 'mean',
    'temp_min': 'mean',
    'precipitation': 'mean'
}).reset_index()
monthly_data = monthly_data.rename(columns={'date': 'month'})

fig, ax1 = plt.subplots()

ax1.fill_between(monthly_data['month'], monthly_data['temp_max'], monthly_data['temp_min'])
ax1.set_ylabel('Avg. Temperature (°C)')
ax1.tick_params(axis='y')

ax2 = ax1.twinx()
ax2.plot(monthly_data['month'], monthly_data['precipitation'], linestyle='-')
ax2.set_ylabel('Precipitation (inches)')
ax2.tick_params(axis='y')

ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

plt.show()