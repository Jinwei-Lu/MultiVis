import altair as alt
import pandas as pd

data = {
    'variety': ['Manchuria', 'Manchuria', 'Manchuria', 'Glabron', 'Glabron', 'Glabron', 'Peatland', 'Peatland', 'Peatland', 'Svansota', 'Svansota', 'Svansota', 'Velvet', 'Velvet', 'Velvet', 'Trebi', 'Trebi', 'Trebi'],
    'site': ['Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm', 'Grand Rapids', 'Morris', 'University Farm'],
    'yield': [27.00, 48.87, 28.70, 27.43, 50.31, 31.99, 27.66, 49.32, 29.47, 27.88, 51.49, 31.32, 28.12, 51.66, 30.35, 28.32, 52.08, 31.12]
}
source = pd.DataFrame(data)

alt.Chart(source).mark_bar().encode(
    x=alt.X('sum(yield):Q', stack="normalize"),
    y=alt.Y('variety:N'),
    color=alt.Color('site:N')
)