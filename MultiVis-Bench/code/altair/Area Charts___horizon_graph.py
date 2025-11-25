import altair as alt
import pandas as pd
import numpy as np

x = np.arange(1, 21)
y = np.random.randint(10, 100, size=20)
ny = y - 50

source = pd.DataFrame({'x': x, 'y': y, 'ny': ny})

base = alt.Chart(source).encode(
    alt.X('x:Q', scale=alt.Scale(zero=False, nice=False))
)

area1 = base.mark_area().encode(
    alt.Y('y:Q', scale=alt.Scale(domain=[0, 50]))
)

area2 = base.mark_area().encode(
    alt.Y('ny:Q', scale=alt.Scale(domain=[-50, 0]))
)

alt.vconcat(area1, area2)