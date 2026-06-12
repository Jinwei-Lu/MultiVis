import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
imdb_rating = np.random.rand(100) * 10
us_gross = np.random.rand(100) * 1000 + imdb_rating * 50
worldwide_gross = np.random.rand(100) * 2000 + imdb_rating * 100

data = pd.DataFrame({'IMDB_Rating': imdb_rating, 'US_Gross': us_gross, 'Worldwide_Gross': worldwide_gross})
data_melted = data.melt('IMDB_Rating', var_name='Gross_Type', value_name='Gross_Value')

alt.Chart(data_melted).mark_line(point=True).encode(
    alt.X('IMDB_Rating:Q').bin(True),
    alt.Y('mean(Gross_Value):Q'),
    color='Gross_Type:N'
)