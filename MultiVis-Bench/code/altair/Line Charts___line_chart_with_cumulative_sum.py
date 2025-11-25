import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
years = np.arange(1810, 1940, 10)
wheat_production = np.random.randint(10, 100, size=len(years))

source = pd.DataFrame({'year': years, 'wheat': wheat_production})

alt.Chart(source).mark_line(point=True).transform_window(
    sort=[{'field': 'year'}],
    frame=[None, 0],
    cumulative_wheat='sum(wheat)'
).encode(
    x=alt.X('year:O'),
    y=alt.Y('cumulative_wheat:Q')
)