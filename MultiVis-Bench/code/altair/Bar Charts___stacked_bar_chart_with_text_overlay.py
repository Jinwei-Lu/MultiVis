import altair as alt
import pandas as pd

data = pd.DataFrame({
    'variety': ['Manchuria', 'Manchuria', 'Manchuria', 'Glabron', 'Glabron', 'Glabron', 'Trebi', 'Trebi', 'Trebi'],
    'site': ['Morris', 'Crookston', 'Grand Rapids', 'Morris', 'Crookston', 'Grand Rapids', 'Morris', 'Crookston', 'Grand Rapids'],
    'yield': [27.0, 31.0, 29.0, 28.0, 33.0, 31.5, 25.5, 29.5, 27.5]
})

bars = alt.Chart(data).mark_bar().encode(
    x=alt.X('sum(yield):Q').stack('zero'),
    y=alt.Y('variety:N'),
    color=alt.Color('site:N')
)

text = alt.Chart(data).mark_text(dx=-15, dy=3).encode(
    x=alt.X('sum(yield):Q').stack('zero'),
    y=alt.Y('variety:N'),
    detail='site:N',
    text=alt.Text('sum(yield):Q', format='.1f')
)

chart = bars + text