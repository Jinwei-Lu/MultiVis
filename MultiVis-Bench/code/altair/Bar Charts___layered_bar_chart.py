import altair as alt
import pandas as pd
import numpy as np

years = np.arange(2010, 2021)
sources = ['Coal', 'Nuclear', 'Natural Gas']
data = []
for year in years:
    for source in sources:
        data.append({'year': year, 'source': source, 'net_generation': np.random.randint(500, 2000)})
df = pd.DataFrame(data)

chart = alt.Chart(df).mark_bar().encode(
    x='year:O',
    y='net_generation:Q',
    color='source:N'
)

chart