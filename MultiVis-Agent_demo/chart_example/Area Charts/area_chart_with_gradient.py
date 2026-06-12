import altair as alt
import pandas as pd
import numpy as np

date_rng = pd.date_range(start='2000-01-01', end='2010-01-01', freq='M')
price = np.random.rand(len(date_rng)) * 100 + 500
data = pd.DataFrame({'date': date_rng, 'price': price, 'symbol': 'GOOG'})

alt.Chart(data).mark_area().encode(
    x='date:T',
    y='price:Q'
)