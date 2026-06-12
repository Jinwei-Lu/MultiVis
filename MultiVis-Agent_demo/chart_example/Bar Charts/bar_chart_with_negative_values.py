import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
months = pd.date_range(start='2006-01-01', end='2010-12-01', freq='MS')
nonfarm_change = np.random.randn(len(months)) * 5000

df = pd.DataFrame({'month': months, 'nonfarm_change': nonfarm_change})

chart = alt.Chart(df).mark_bar().encode(
    x='month:T',
    y='nonfarm_change:Q'
)

chart