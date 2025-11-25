import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(0)
dates = pd.date_range('2023-01-01', periods=50)
symbols = ['AAPL', 'GOOG', 'MSFT']
data = []
for symbol in symbols:
    base_price = np.random.randint(100, 300)
    prices = base_price + np.cumsum(np.random.randn(50) * 5)
    for i in range(50):
        data.append({'date': dates[i], 'price': prices[i], 'symbol': symbol})

source = pd.DataFrame(data)

fig, ax = plt.subplots()

for symbol in source['symbol'].unique():
    symbol_data = source[source['symbol'] == symbol]
    ax.plot(symbol_data['date'], symbol_data['price'], label=symbol)

ax.set_xlabel('date')
ax.set_ylabel('price')
ax.legend()

fig.autofmt_xdate()

plt.show()