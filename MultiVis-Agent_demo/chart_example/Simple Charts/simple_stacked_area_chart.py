import altair as alt
import pandas as pd
import numpy as np

years = np.arange(2001, 2019)
sources = ['Coal', 'Natural Gas', 'Nuclear']
data = []
for year in years:
    for source in sources:
        net_generation = np.random.randint(1000, 5000) + (year - 2001) * 100
        if source == 'Coal':
            net_generation *= 1.5
        elif source == 'Natural Gas':
            net_generation *= 0.8
        data.append({'year': year, 'source': source, 'net_generation': net_generation})
df = pd.DataFrame(data)

chart = alt.Chart(df).mark_area().encode(
    x="year:T",
    y="net_generation:Q",
    color="source:N"
)

chart