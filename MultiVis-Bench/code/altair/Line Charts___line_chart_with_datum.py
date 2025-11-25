import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)
dates = pd.date_range(start='2005-01-01', end='2007-01-01', freq='M')
symbols = ['AAPL', 'GOOG', 'MSFT']
data = []
for symbol in symbols:
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 10)
    for i in range(len(dates)):
        data.append({'date': dates[i], 'price': prices[i], 'symbol': symbol})
source = pd.DataFrame(data)

lines = (
    alt.Chart(source)
    .mark_line()
    .encode(
        x="date:T",
        y="price:Q",
        color="symbol:N"
    )
)

xrule = (
    alt.Chart()
    .mark_rule()
    .encode(x=alt.datum(alt.DateTime(year=2006, month="November")))
)

yrule = (
    alt.Chart().mark_rule(strokeDash=[12, 6]).encode(y=alt.datum(350))
)

chart = lines + yrule + xrule
chart