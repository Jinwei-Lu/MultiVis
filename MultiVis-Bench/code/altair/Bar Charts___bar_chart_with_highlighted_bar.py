import altair as alt
import pandas as pd
import numpy as np

years = np.arange(1790, 1880, 10)
wheat = np.random.randint(20, 80, size=len(years))
source = pd.DataFrame({'year': years, 'wheat': wheat})

alt.Chart(source).mark_bar().encode(
    x=alt.X("year:O"),
    y=alt.Y("wheat:Q"),
    color=alt.condition(
        alt.datum.year == 1810,
        alt.value("orange"),
        alt.value("steelblue")
    )
)