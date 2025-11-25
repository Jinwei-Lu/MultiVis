import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)
num_flights = 5000
time_data = np.random.rand(num_flights) * 24

source = pd.DataFrame({'time': time_data})

brush = alt.selection_interval(encodings=['x'])

base = alt.Chart(source).mark_bar().encode(
    y='count():Q'
)

top_hist = base.encode(
    alt.X('time:Q')
      .bin(maxbins=30, extent=brush)
      .scale(domain=brush)
)

bottom_hist = base.encode(
    alt.X('time:Q').bin(maxbins=30),
).add_params(
    brush
)

chart = alt.vconcat(top_hist, bottom_hist).resolve_scale(
    x='independent'
)

chart