import altair as alt
import pandas as pd

data_list = [
    {'Horsepower': 150, 'Miles_per_Gallon': 25, 'Origin': 'USA'},
    {'Horsepower': 100, 'Miles_per_Gallon': 30, 'Origin': 'Japan'},
    {'Horsepower': 200, 'Miles_per_Gallon': 20, 'Origin': 'USA'},
    {'Horsepower': 80, 'Miles_per_Gallon': 35, 'Origin': 'Japan'},
    {'Horsepower': 180, 'Miles_per_Gallon': 22, 'Origin': 'USA'},
    {'Horsepower': 120, 'Miles_per_Gallon': 28, 'Origin': 'Europe'},
    {'Horsepower': 250, 'Miles_per_Gallon': 15, 'Origin': 'USA'},
    {'Horsepower': 90, 'Miles_per_Gallon': 32, 'Origin': 'Japan'},
    {'Horsepower': 160, 'Miles_per_Gallon': 24, 'Origin': 'USA'},
    {'Horsepower': 110, 'Miles_per_Gallon': 29, 'Origin': 'Europe'},
    {'Horsepower': 130, 'Miles_per_Gallon': 27, 'Origin': 'USA'},
    {'Horsepower': 170, 'Miles_per_Gallon': 23, 'Origin': 'Japan'},
    {'Horsepower': 220, 'Miles_per_Gallon': 18, 'Origin': 'USA'},
    {'Horsepower': 70, 'Miles_per_Gallon': 38, 'Origin': 'Japan'},
    {'Horsepower': 190, 'Miles_per_Gallon': 21, 'Origin': 'USA'},
    {'Horsepower': 140, 'Miles_per_Gallon': 26, 'Origin': 'Europe'},
    {'Horsepower': 240, 'Miles_per_Gallon': 16, 'Origin': 'USA'},
    {'Horsepower': 85, 'Miles_per_Gallon': 33, 'Origin': 'Japan'},
    {'Horsepower': 155, 'Miles_per_Gallon': 24.5, 'Origin': 'USA'},
    {'Horsepower': 115, 'Miles_per_Gallon': 28.5, 'Origin': 'Europe'},
    {'Horsepower': 210, 'Miles_per_Gallon': 19, 'Origin': 'USA'},
    {'Horsepower': 95, 'Miles_per_Gallon': 31, 'Origin': 'Japan'},
    {'Horsepower': 175, 'Miles_per_Gallon': 22.5, 'Origin': 'USA'},
    {'Horsepower': 125, 'Miles_per_Gallon': 27.5, 'Origin': 'Europe'},
    {'Horsepower': 230, 'Miles_per_Gallon': 17, 'Origin': 'USA'},
    {'Horsepower': 75, 'Miles_per_Gallon': 36, 'Origin': 'Japan'},
    {'Horsepower': 185, 'Miles_per_Gallon': 21.5, 'Origin': 'USA'},
    {'Horsepower': 135, 'Miles_per_Gallon': 26.5, 'Origin': 'Europe'}
]
source = pd.DataFrame(data_list)

brush = alt.selection_interval()

points = alt.Chart(source).mark_point().encode(
    x='Horsepower:Q',
    y='Miles_per_Gallon:Q',
    color=alt.condition(brush, alt.value("steelblue"), alt.value("grey"))
).add_params(brush)

ranked_text = alt.Chart(source).mark_text().encode(
    y=alt.Y('row_number:O')
).transform_filter(
    brush
).transform_window(
    row_number='row_number()'
).transform_filter(
    alt.datum.row_number < 15
)

horsepower = ranked_text.encode(text='Horsepower:N')
mpg = ranked_text.encode(text='Miles_per_Gallon:N')
origin = ranked_text.encode(text='Origin:N')
text = alt.hconcat(horsepower, mpg, origin)

chart = alt.hconcat(points, text)
chart