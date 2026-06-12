import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)
dates = pd.date_range(start='2020-01-01', end='2022-12-01', freq='MS')
counts = 100 + np.cumsum(np.random.randn(len(dates)) * 10)
counts = np.maximum(counts, 0)

data = pd.DataFrame({'date': dates, 'count': counts})
source = data

base = alt.Chart(source).mark_area().encode(
    x='yearmonth(date):T',
    y='sum(count):Q',
)

brush = alt.selection_interval(encodings=['x'])
background = base.add_params(brush)
selected = base.transform_filter(brush)

background + selected