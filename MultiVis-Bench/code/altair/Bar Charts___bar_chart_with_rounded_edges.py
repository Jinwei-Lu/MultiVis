import altair as alt
import pandas as pd

data = [
    {'date': '2023-01-01', 'weather': 'sun'},
    {'date': '2023-01-05', 'weather': 'rain'},
    {'date': '2023-02-10', 'weather': 'sun'},
    {'date': '2023-02-15', 'weather': 'snow'}
]

source = pd.DataFrame(data)

alt.Chart(source).mark_bar().encode(
    x='month(date):O',
    y='count():Q',
    color='weather:N'
)