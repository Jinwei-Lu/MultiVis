import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(0)
dates = pd.date_range('2023-01-01', periods=100, freq='D')
prices = 100 + np.cumsum(np.random.randn(100))
data = pd.DataFrame({'date': dates, 'price': prices, 'symbol': ['GOOG'] * 100})

source_goog = data[data['symbol'] == 'GOOG']

fig, ax = plt.subplots()

ax.fill_between(source_goog['date'], source_goog['price'], step='post')
ax.plot(source_goog['date'], source_goog['price'], linestyle='-', drawstyle='steps-post')

ax.set_xlabel('date')
ax.set_ylabel('price')

fig.autofmt_xdate()

plt.show()