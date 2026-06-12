import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)

n_varieties = 3
n_sites = 6
n_years = 2

varieties = [f'Variety_{i+1}' for i in range(n_varieties)]
sites = [f'Site_{i+1}' for i in range(n_sites)]
years = [2022, 2023]

data = []
for variety in varieties:
    for site in sites:
      for year in years:
        data.append({'variety': variety, 'site': site, 'year': year, 'yield': np.random.randint(10, 50)})

source = pd.DataFrame(data)

alt.Chart(source).mark_bar().encode(
    x=alt.X('sum(yield):Q'),
    y=alt.Y('variety:N'),
    color=alt.Color('site:N'),
    order=alt.Order('site', sort='ascending')
)