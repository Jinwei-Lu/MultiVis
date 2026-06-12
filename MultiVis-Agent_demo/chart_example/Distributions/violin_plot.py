import altair as alt
import pandas as pd
import numpy as np

europe_mpg = np.concatenate([
    np.random.normal(28, 5, 150),
    np.random.normal(40, 3, 50),
    np.random.normal(18, 3, 30)
])
japan_mpg = np.concatenate([
    np.random.normal(32, 6, 180),
    np.random.normal(45, 4, 70),
    np.random.normal(25, 2, 20)
])
usa_mpg = np.concatenate([
    np.random.normal(22, 4, 200),
    np.random.normal(15, 3, 50),
    np.random.normal(35, 2, 10)
])

europe_df = pd.DataFrame({'Miles_per_Gallon': europe_mpg, 'Origin': 'Europe'})
japan_df = pd.DataFrame({'Miles_per_Gallon': japan_mpg, 'Origin': 'Japan'})
usa_df = pd.DataFrame({'Miles_per_Gallon': usa_mpg, 'Origin': 'USA'})
data = pd.concat([europe_df, japan_df, usa_df])

chart = alt.Chart(data).transform_density(
    'Miles_per_Gallon',
    as_=['Miles_per_Gallon', 'density'],
    extent=[5, 50],
    groupby=['Origin']
).mark_area(orient='horizontal').encode(
    alt.X('density:Q').stack('center'),
    alt.Y('Miles_per_Gallon:Q'),
    alt.Color('Origin:N'),
    alt.Column('Origin:N')
)

chart.show()