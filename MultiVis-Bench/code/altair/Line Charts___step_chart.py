import altair as alt
import pandas as pd
import numpy as np

date_range = pd.date_range(start='2000-01-01', end='2010-12-31', freq='M')
num_dates = len(date_range)
prices = 100 + np.cumsum(np.random.randn(num_dates) * 5)
data = pd.DataFrame({'date': date_range, 'price': prices})

alt.Chart(data).mark_line(interpolate='step-after').encode(
    x='date:T',
    y='price:Q'
).properties(
    title='Stock Price Over Time'
)