import altair as alt
import numpy as np
import pandas as pd

imdb_ratings = np.random.normal(loc=7.0, scale=1.5, size=1000)
imdb_ratings = np.clip(imdb_ratings, 0, 10)

df = pd.DataFrame({'ratings': imdb_ratings})

chart = alt.Chart(df).mark_bar().encode(
    alt.X("ratings:Q", bin=True),
    y='count()',
    tooltip=['count()', alt.Tooltip('ratings:Q', bin=True)]
).properties(
    title='IMDB Ratings Distribution'
)

chart