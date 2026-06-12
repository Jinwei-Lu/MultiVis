import altair as alt
import numpy as np
import pandas as pd

years = np.arange(1810, 1911)
base_production = 20
growth_rate = 0.8
random_variation = 5

wheat_production = base_production + growth_rate * (years - 1810) + np.random.normal(0, random_variation, len(years))
wheat_production = np.maximum(0, wheat_production)

source = pd.DataFrame({
    'year': years,
    'wheat': wheat_production
})

alt.Chart(source).mark_trail().encode(
    x='year:T',
    y='wheat:Q',
    size='wheat:Q'
)