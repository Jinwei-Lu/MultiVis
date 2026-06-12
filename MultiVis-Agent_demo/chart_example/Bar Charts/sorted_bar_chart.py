import altair as alt
import pandas as pd

data = {'site': ['Site A', 'Site B', 'Site C', 'Site D', 'Site E'],
        'yield': [50, 80, 60, 90, 70],
        'variety': ['Variety1', 'Variety2', 'Variety3', 'Variety4', 'Variety5'],
        'year': [1930, 1931, 1932, 1933, 1934]}
source = pd.DataFrame(data)

chart = alt.Chart(source).mark_bar().encode(
    x='sum(yield):Q',
    y=alt.Y('site:N').sort('-x')
)

chart.show()