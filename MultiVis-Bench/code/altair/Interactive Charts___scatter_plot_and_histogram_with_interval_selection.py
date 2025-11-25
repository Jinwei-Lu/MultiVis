import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
x = np.random.uniform(0, 10, size=100)
y = np.random.uniform(0, 10, size=100)
m = np.random.normal(5, 2, size=100)

source = pd.DataFrame({"x": x, "y": y, "m": m})

pts = alt.selection_interval(encodings=["x"])

points = alt.Chart().mark_point().encode(
    x='x',
    y='y'
).transform_filter(
    pts
)

mag = alt.Chart().mark_bar().encode(
    x='mbin:N',
    y="count()"
).add_params(pts)

alt.hconcat(
    points,
    mag,
    data=source
).transform_bin(
    "mbin",
    field="m",
    bin=alt.Bin(maxbins=20)
)