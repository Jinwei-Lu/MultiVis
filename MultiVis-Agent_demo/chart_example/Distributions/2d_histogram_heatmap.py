import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)

imdb_ratings = np.random.normal(loc=6.5, scale=1.5, size=1000)
rotten_tomatoes_ratings = np.random.normal(loc=60, scale=15, size=1000)

imdb_ratings = np.clip(imdb_ratings, 0, 10)
rotten_tomatoes_ratings = np.clip(rotten_tomatoes_ratings, 0, 100)

df = pd.DataFrame({
    'IMDB_Rating': imdb_ratings,
    'Rotten_Tomatoes_Rating': rotten_tomatoes_ratings
})

chart = alt.Chart(df).mark_rect().encode(
    alt.X('IMDB_Rating:Q').bin(maxbins=60),
    alt.Y('Rotten_Tomatoes_Rating:Q').bin(maxbins=40),
    alt.Color('count():Q')
)

chart