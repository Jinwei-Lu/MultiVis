import altair as alt
import pandas as pd
import numpy as np

dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
precipitation = 2 + np.sin(2 * np.pi * (dates.dayofyear / 365)) * 1.5 + np.random.randn(len(dates)) * 0.5
precipitation = np.maximum(precipitation, 0)

source = pd.DataFrame({'date': dates, 'precipitation': precipitation})

brush = alt.selection_interval(encodings=['x'])

bars = alt.Chart(source).mark_bar().encode(
    x='month(date):O',
    y='mean(precipitation):Q',
    opacity=alt.condition(brush, alt.value(1), alt.value(0.7)),
).add_params(
    brush
)

line = alt.Chart(source).mark_rule().encode(
    y='mean(precipitation):Q',
).transform_filter(
    brush
)

alt.layer(bars, line)