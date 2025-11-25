import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

dates = pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'])
symbols = ['AAPL', 'GOOG', 'MSFT']

data = []
for symbol in symbols:
    for date in dates:
        price = 100 + np.random.randn() * 5 + (date - dates[0]).days * 2
        data.append({'date': date, 'price': price, 'symbol': symbol})

source = pd.DataFrame(data)

fig, ax = plt.subplots()

for symbol in source['symbol'].unique():
    symbol_data = source[source['symbol'] == symbol]
    ax.plot(symbol_data['date'], symbol_data['price'])

ax.set_xlabel('date')
ax.set_ylabel('price')

plt.show()