import altair as alt
import pandas as pd
import numpy as np

years = ['1931', '1932']
sites = ['University Farm', 'Waseca', 'Morris', 'Grand Rapids', 'Crookston', 'Duluth']

data = []
for site in sites:
    for year in years:
        data.append({
            'site': site,
            'year': year,
            'yield': np.random.randint(20, 80)
        })
df = pd.DataFrame(data)

chart = alt.Chart(df).mark_bar().encode(
    x='year:O',
    y='sum(yield):Q',
    color='year:N',
    column='site:N'
)

chart