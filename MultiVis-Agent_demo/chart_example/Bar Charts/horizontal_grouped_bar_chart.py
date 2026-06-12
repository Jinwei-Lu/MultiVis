import altair as alt
import numpy as np
import pandas as pd

years = np.arange(1880, 1940, 5)
wheat_production = np.random.randint(50, 300, size=len(years))
source = pd.DataFrame({'year': years, 'wheat': wheat_production})

chart = alt.Chart(source).mark_bar().encode(
    x='wheat:Q',
    y='year:O'
)

chart