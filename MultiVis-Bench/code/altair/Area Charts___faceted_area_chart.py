import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
date_rng = pd.date_range(start='1/1/2000', end='1/1/2010', freq='M')
symbols = ["MSFT", "AAPL", "IBM", "AMZN"]
data = {}
for symbol in symbols:
    data[symbol] = np.random.rand(len(date_rng)).cumsum() + 10

df = pd.DataFrame(data, index=date_rng)
df = df.stack().reset_index()
df.columns = ['date', 'symbol', 'price']

chart = alt.Chart(df).mark_area(opacity=0.7).encode(
    x="date:T",
    y="price:Q",
    color="symbol:N",
    row="symbol:N"
)
chart