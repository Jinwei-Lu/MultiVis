import altair as alt
import pandas as pd

source = pd.DataFrame({
    "data": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             2, 2, 2,
             3, 3,
             4, 4, 4, 4, 4, 4]
})

chart = alt.Chart(source).mark_circle().transform_window(
    id='rank()',
    groupby=['data']
).encode(
    x='data:O',
    y=alt.Y('id:O', sort='descending')
)

chart