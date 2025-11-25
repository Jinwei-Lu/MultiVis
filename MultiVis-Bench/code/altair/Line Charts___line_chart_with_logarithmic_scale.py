import altair as alt
import pandas as pd
import numpy as np

years = np.arange(1800, 2001, 10)
population = 1000 * np.exp(0.02 * (years - 1800)) * (1 + 0.1 * np.random.randn(len(years)))
population = population.astype(int)

source = pd.DataFrame({'year': years, 'people': population})

alt.Chart(source).mark_line().encode(
    x='year:O',
    y='sum(people)'
)