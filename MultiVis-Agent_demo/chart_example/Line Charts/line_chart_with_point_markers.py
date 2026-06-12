import altair as alt
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

chart = alt.Chart(source).mark_line(point=True).encode(
    x='date:T',
    y='price:Q',
    color='symbol:N'
)

chart.show()