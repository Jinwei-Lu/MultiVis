import altair as alt
import pandas as pd

source = pd.DataFrame({
    'x': [1, 3, 5, 7, 9],
    'y': [2, 4, 1, 8, 6],
    'label': ['A', 'B', 'C', 'D', 'E']
})

points = alt.Chart(source).mark_point().encode(
    x='x:Q',
    y='y:Q'
)

text = alt.Chart(source).mark_text().encode(
    x='x:Q',
    y='y:Q',
    text='label:N'
)

chart = points + text

chart.display()