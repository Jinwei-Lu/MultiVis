import altair as alt
import pandas as pd
import numpy as np

years = list(range(1930, 1939))
wheat = np.random.randint(100, 500, size=len(years))
wages = np.random.randint(20, 100, size=len(years))

source = pd.DataFrame({
    'year': years,
    'wheat': wheat,
    'wages': wages
})

base = alt.Chart(source).encode(
    alt.X('year:O')
)

bar = base.mark_bar().encode(
    alt.Y('wheat:Q')
)

line = base.mark_line().encode(
    alt.Y('wages:Q')
)

chart = bar + line
chart