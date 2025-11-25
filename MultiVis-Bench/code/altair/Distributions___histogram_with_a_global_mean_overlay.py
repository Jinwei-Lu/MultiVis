import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
imdb_ratings = np.random.normal(loc=7.0, scale=1.5, size=1000)
imdb_ratings = np.clip(imdb_ratings, 0, 10)

data = pd.DataFrame({'IMDB_Rating': imdb_ratings})

base = alt.Chart(data)

bar = base.mark_bar().encode(
    alt.X('IMDB_Rating:Q', bin=True),
    alt.Y('count():Q')
)

rule = base.mark_rule().encode(
    alt.X('mean(IMDB_Rating):Q')
)

bar + rule