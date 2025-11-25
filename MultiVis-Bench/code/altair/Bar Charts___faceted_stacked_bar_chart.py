import altair as alt
import pandas as pd
import numpy as np

varieties = ['Wisconsin No. 38', 'Velvet', 'Trebi', 'Svansota', 'Peatland', 'No. 475', 'No. 462', 'No. 457', 'Manchuria', 'Glabron']
sites = ['Waseca', 'University Farm', 'Morris', 'Grand Rapids', 'Duluth', 'Crookston']
years = ['1931', '1932']

rng = np.random.default_rng(42)

data = []
for year in years:
    for variety in varieties:
        for i, site in enumerate(sites):
            yield_value = rng.integers(0, 60)
            data.append({'variety': variety, 'site': site, 'year': year, 'yield': yield_value})

df = pd.DataFrame(data)

chart = alt.Chart(df).mark_bar().encode(
    column=alt.Column("year:O"),
    x=alt.X("yield:Q"),
    y=alt.Y("variety:N"),
    color=alt.Color("site:N")
)

chart