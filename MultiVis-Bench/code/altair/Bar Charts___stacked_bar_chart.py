import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
varieties = ['A', 'B', 'C']
sites = ['Site1', 'Site2', 'Site3', 'Site4']
data = []
for variety in varieties:
    for site in sites:
        data.append({'variety': variety, 'site': site, 'yield': np.random.randint(20, 80)})

source = pd.DataFrame(data)

alt.Chart(source).mark_bar().encode(
    x='variety',
    y='sum(yield)',
    color='site'
)