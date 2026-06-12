import altair as alt
import pandas as pd
import numpy as np

data = {
    'country': ['China', 'India', 'United States', 'Indonesia', 'Brazil'] * 2,
    'year': [1955] * 5 + [2000] * 5,
    'life_expect': np.random.rand(10) * 30 + 50
}
df = pd.DataFrame(data)

chart = alt.Chart(df).encode(
    x='life_expect:Q',
    y='country:N'
)

line = chart.mark_line().encode(
    detail='country:N'
)

points = chart.mark_point().encode(
    color='year:O'
)

final_chart = (line + points)
final_chart