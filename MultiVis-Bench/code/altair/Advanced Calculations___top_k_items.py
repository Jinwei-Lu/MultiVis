import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
n_movies = 15
data = {
    'Title': [f'Movie {i}' for i in range(1, n_movies + 1)],
    'IMDB_Rating': np.random.uniform(6, 10, n_movies)
}
df = pd.DataFrame(data)

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Title:N', sort='-y'),
    y=alt.Y('IMDB_Rating:Q')
).transform_window(
    rank='rank(IMDB_Rating)',
    sort=[alt.SortField('IMDB_Rating', order='descending')]
).transform_filter(
    alt.datum.rank <= 10
)

chart