import altair as alt
import numpy as np
import pandas as pd

num_movies = 500
imdb_ratings = np.random.uniform(1, 10, num_movies)
imdb_ratings.sort()
cumulative_count = np.arange(1, num_movies + 1)

df = pd.DataFrame({'IMDB_Rating': imdb_ratings, 'cumulative_count': cumulative_count})

alt.Chart(df).mark_area().encode(
    x=alt.X("IMDB_Rating:Q"),
    y=alt.Y("cumulative_count:Q")
)