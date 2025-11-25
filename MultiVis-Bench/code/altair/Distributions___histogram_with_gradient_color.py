import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)
dummy_data = np.clip(np.random.normal(loc=7, scale=1.5, size=5000), 1, 10)
df = pd.DataFrame({'IMDB_Rating': dummy_data})

chart = alt.Chart(df).mark_bar().encode(
    alt.X("IMDB_Rating:Q", bin=alt.Bin(maxbins=20, extent=[1, 10])),
    alt.Y('count()'),
    alt.Color("IMDB_Rating:Q", bin=alt.Bin(maxbins=20, extent=[1, 10]))
)

chart