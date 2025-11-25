import altair as alt
import pandas as pd
import numpy as np

years = range(1990, 2001)
wheat_values = np.random.randint(30, 100, size=len(years))

source = pd.DataFrame({'year': years, 'wheat': wheat_values})

chart = alt.Chart(source).mark_bar().encode(
    y='year:O',
    x='wheat:Q'
)

chart