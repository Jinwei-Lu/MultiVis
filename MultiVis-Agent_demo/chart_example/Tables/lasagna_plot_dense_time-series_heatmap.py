import altair as alt
import pandas as pd
import numpy as np

symbols = ['AAPL', 'AMZN', 'MSFT', 'IBM']
dates = pd.to_datetime(pd.date_range('2000-01-01', '2001-12-31', freq='B'))
data = []
for symbol in symbols:
    for date in dates:
        price = 100 + np.random.randn() * 10 + (date.year - 2000) * 50
        data.append({'symbol': symbol, 'date': date, 'price': price})

source = pd.DataFrame(data)

alt.Chart(source).transform_filter(
    alt.datum.symbol != "GOOG"
).mark_rect().encode(
    alt.X("yearmonthdate(date):O"),
    alt.Y("symbol:N"),
    alt.Color("sum(price)")
)