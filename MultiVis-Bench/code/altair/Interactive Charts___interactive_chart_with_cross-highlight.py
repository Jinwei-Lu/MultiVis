import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 2000

genres = [
    "Action", "Adventure", "Comedy", "Drama", "Horror", "Thriller", "Sci-Fi",
    "Romance", "Fantasy", "Mystery", "Animation", "Documentary"
]

data = pd.DataFrame({
    'IMDB_Rating': np.random.normal(7, 1, n_samples),
    'Rotten_Tomatoes_Rating': np.random.normal(65, 15, n_samples),
    'Major_Genre': np.random.choice(genres, n_samples),
})

data['IMDB_Rating'] = data['IMDB_Rating'].clip(0, 10)
data['Rotten_Tomatoes_Rating'] = data['Rotten_Tomatoes_Rating'].clip(0, 100)

pts = alt.selection_point(encodings=['x'])

rect = alt.Chart(data).mark_rect().encode(
    alt.X('IMDB_Rating:Q').bin(),
    alt.Y('Rotten_Tomatoes_Rating:Q').bin(),
    alt.Color('count()')
)

circ = rect.mark_point().encode(
    alt.Size('count()')
).transform_filter(
    pts
)

bar = alt.Chart(data).mark_bar().encode(
    x='Major_Genre:N',
    y='count()',
    color=alt.condition(pts, alt.ColorValue("steelblue"), alt.ColorValue("grey"))
).add_params(pts)

alt.vconcat(
    rect + circ,
    bar
)