import altair as alt
import pandas as pd
import numpy as np

years = np.arange(2001, 2018)
sources = ['Coal', 'Natural Gas', 'Nuclear']
data = []
for year in years:
    gen = np.random.rand(len(sources)) * 100
    for i, source in enumerate(sources):
        data.append({'year': year, 'source': source, 'net_generation': gen[i]})
df = pd.DataFrame(data)

df_pivot = df.pivot(index='year', columns='source', values='net_generation')
df_normalized = df_pivot.div(df_pivot.sum(axis=1), axis=0)
df_long = df_normalized.reset_index().melt(id_vars='year', var_name='source', value_name='normalized_generation')

chart = alt.Chart(df_long).mark_area().encode(
    x=alt.X("year:T"),
    y=alt.Y("normalized_generation:Q", stack="normalize"),
    color=alt.Color("source:N")
)

chart.show()