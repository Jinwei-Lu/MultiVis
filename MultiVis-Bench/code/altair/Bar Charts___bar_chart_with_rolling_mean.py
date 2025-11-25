import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
years = np.arange(1810, 1911, 10)
wheat_production = np.random.randint(20, 60, size=len(years)) + np.sin(np.linspace(0, 10, len(years))) * 20
data = pd.DataFrame({'year': years, 'wheat': wheat_production})

data['rolling_mean'] = data['wheat'].rolling(window=10, min_periods=1).mean()

bar = alt.Chart(data).mark_bar().encode(
    x=alt.X('year:O'),
    y=alt.Y('wheat:Q')
)

line = alt.Chart(data).mark_line().encode(
    x=alt.X('year:O'),
    y=alt.Y('rolling_mean:Q')
)

chart = (bar + line)

chart