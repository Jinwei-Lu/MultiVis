import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(42)
n_days = 100
dates = pd.date_range('2023-01-01', periods=n_days, freq='D')
symbols = ['AAPL', 'MSFT', 'GOOG']
data = {}
for symbol in symbols:
    data[symbol] = np.cumsum(np.random.randn(n_days)) + 100

df = pd.DataFrame(data, index=dates)
df = df.stack().reset_index()
df.columns = ['date', 'symbol', 'price']

fig, ax = plt.subplots()

for symbol in symbols:
    subset = df[df['symbol'] == symbol]
    ax.plot(subset['date'], subset['price'])

for symbol in symbols:
    subset = df[df['symbol'] == symbol]
    last_date = subset['date'].iloc[-1]
    last_price = subset['price'].iloc[-1]
    ax.plot(last_date, last_price, 'o')
    ax.text(last_date, last_price, f' {symbol}', va='center', ha='left')

ax.set_xlabel('Date')
ax.set_ylabel('Price')

plt.show()