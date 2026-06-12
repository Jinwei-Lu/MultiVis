import altair as alt
import pandas as pd
import numpy as np

years = ['1931', '1932'] * 6
sites = ['Grand Rapids', 'Duluth', 'University Farm', 'Morris', 'Crookston', 'Waseca'] * 2
np.random.seed(42)

yields = []
for site in ['Grand Rapids', 'Duluth', 'University Farm', 'Morris', 'Crookston', 'Waseca']:
    yields.extend(np.random.normal(loc=30, scale=5, size=1) + np.random.randint(-5,6,size=1))
    yields.extend(np.random.normal(loc=35, scale=7, size=1) + np.random.randint(-5, 6, size=1))

df = pd.DataFrame({'year': years, 'site': sites, 'yield': yields})
df['year'] = df['year'].astype('category')

bars = alt.Chart(df).mark_bar().encode(
    x='year:N',
    y='mean(yield):Q'
)

error_bars = alt.Chart(df).mark_errorbar(extent='stdev').encode(
    x='year:N',
    y='yield:Q'
)

chart = alt.layer(bars, error_bars).facet(
    column='site:N'
)

chart.display()