import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
num_points = 500

release_dates = np.random.randint(1930, 2011, num_points)
rating_deltas = []

for year in release_dates:
    if year < 1970:
        rating_delta = np.random.uniform(-1, 2)
    elif year < 1990:
        rating_delta = np.random.uniform(-2, 2.5)
    else:
        rating_delta = np.random.uniform(-4, 3)
    rating_deltas.append(rating_delta)

df = pd.DataFrame({'Release Date': release_dates, 'Rating Delta': rating_deltas})

chart = alt.Chart(df).mark_point().encode(
    x=alt.X('Release Date:Q', scale=alt.Scale(domain=(1928, 2012))),
    y=alt.Y('Rating Delta:Q', scale=alt.Scale(domain=(-5, 3))),
    color=alt.Color('Rating Delta:Q')
).properties(
    title='Rating Delta vs. Release Date'
)

chart