import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime

np.random.seed(0)
dates = pd.date_range(start='2005-01-01', end='2007-01-01', freq='M')
symbols = ['AAPL', 'GOOG', 'MSFT']
data = []
for symbol in symbols:
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 10)
    for i in range(len(dates)):
        data.append({'date': dates[i], 'price': prices[i], 'symbol': symbol})
source = pd.DataFrame(data)

fig, ax = plt.subplots()

for symbol in symbols:
    symbol_data = source[source['symbol'] == symbol]
    ax.plot(symbol_data['date'], symbol_data['price'])

xrule_date = datetime.datetime(2006, 11, 1)
ax.axvline(x=xrule_date)

ax.axhline(y=350)

ax.set_xlabel('date')
ax.set_ylabel('price')

plt.show()