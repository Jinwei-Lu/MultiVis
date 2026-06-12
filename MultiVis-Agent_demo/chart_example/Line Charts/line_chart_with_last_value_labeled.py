import altair as alt
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

chart = alt.Chart(df).transform_filter(
    alt.datum.symbol != "IBM"
).encode(
    alt.Color("symbol").legend(None)
)

line = chart.mark_line().encode(
    x="date:T",
    y="price:Q"
)

label = chart.encode(
    x='max(date):T',
    y=alt.Y('price:Q').aggregate(argmax='date'),
    text='symbol'
)

text = label.mark_text()
circle = label.mark_circle()

line + circle + text