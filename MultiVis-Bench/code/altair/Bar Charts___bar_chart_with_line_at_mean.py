import altair as alt
import pandas as pd
import numpy as np

years = [str(year) for year in range(1950, 1960)]
wheat_values = np.random.randint(500, 1000, size=len(years))

source = pd.DataFrame({'year': years, 'wheat': wheat_values})

bar = alt.Chart(source).mark_bar().encode(
    x='year:O',
    y='wheat:Q'
)

rule = alt.Chart(source).mark_rule().encode(
    y='mean(wheat):Q'
)

chart = bar + rule
chart