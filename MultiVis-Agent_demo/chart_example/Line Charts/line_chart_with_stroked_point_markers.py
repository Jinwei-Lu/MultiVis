import altair as alt
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

chart = alt.Chart(source).mark_line(point=True).encode(
    x='date:T',
    y='price:Q',
    color='symbol:N'
)

chart.show()