import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(0)
dates = pd.to_datetime(pd.date_range('2023-01-01', periods=30, freq='D'))
symbols = ['AAPL', 'GOOG', 'MSFT']
data = []
for symbol in symbols:
    prices = 100 + np.cumsum(np.random.randn(30)) * 2
    for date, price in zip(dates, prices):
        data.append({'date': date, 'price': price, 'symbol': symbol})

source = pd.DataFrame(data)

fig, ax = plt.subplots()

for symbol in symbols:
    symbol_data = source[source['symbol'] == symbol]
    ax.plot(symbol_data['date'], symbol_data['price'], label=symbol)

ax.set_xlabel('Date')
ax.set_ylabel('Price')

ax.legend()

plt.show()