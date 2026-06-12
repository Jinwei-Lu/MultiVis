import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
varieties = ['A', 'B', 'C', 'D', 'E']
years = [2020, 2021, 2022]
sites = ['Site1', 'Site2', 'Site3']

data = []
for variety in varieties:
    for year in years:
        for site in sites:
            yield_val = np.random.normal(loc=30 + (ord(variety) - ord('A')) * 5, scale=10)
            data.append([variety, year, site, yield_val])

source = pd.DataFrame(data, columns=['variety', 'year', 'site', 'yield'])

error_bars = alt.Chart(source).mark_errorbar(extent='ci').encode(
    x=alt.X('yield:Q', scale=alt.Scale(zero=False)),
    y=alt.Y('variety:N')
)

points = alt.Chart(source).mark_point().encode(
    x=alt.X('mean(yield):Q'),
    y=alt.Y('variety:N')
)

chart = error_bars + points

chart