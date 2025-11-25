import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime

date_rng = pd.date_range(start='2000-01-01', end='2010-01-01', freq='M')
price = np.random.rand(len(date_rng)) * 100 + 500
data = pd.DataFrame({'date': date_rng, 'price': price})

data['date'] = pd.to_datetime(data['date'])
dates = mdates.date2num(data['date'])

fig, ax = plt.subplots()

ax.fill_between(dates, data['price'], color='darkgreen', alpha=0.5)
ax.plot(dates, data['price'], color='darkgreen')

ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45, ha='right')

ax.set_xlabel('Date')
ax.set_ylabel('Price')

plt.show()