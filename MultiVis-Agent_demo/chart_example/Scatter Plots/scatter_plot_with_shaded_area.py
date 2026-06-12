import altair as alt
import pandas as pd
import numpy as np

data = pd.DataFrame({
    "x": np.random.uniform(-4, 5, size=50),
    "y": np.random.uniform(2, 5, size=50),
})

df = pd.DataFrame({
    "x": range(7),
    "ymin": range(7),
    "ymax": range(1, 8)
})

rect_data = pd.DataFrame({
    "x1": [-2],
    "x2": [-1]
})

points = alt.Chart(data).mark_point().encode(
    x='x',
    y='y'
)

interval = alt.Chart(df).mark_area(opacity=0.3).encode(
    x='x:Q',
    y='ymin:Q',
    y2='ymax:Q'
)

rect = alt.Chart(rect_data).mark_rect(opacity=0.3).encode(
    x='x1:Q',
    x2='x2:Q'
)

(points + interval + rect)