import altair as alt
import pandas as pd
import numpy as np

date_range = pd.date_range(start='2000-01-01', end='2010-01-01', freq='M')
num_dates = len(date_range)
prices = np.random.rand(num_dates) * 100 + np.arange(num_dates) * 2
data = pd.DataFrame({'date': date_range, 'price': prices})
data['symbol'] = 'GOOG'

alt.Chart(data).mark_area(
    interpolate='step-after',
    line=True
).encode(
    x='date:T',
    y='price:Q'
)