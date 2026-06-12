import altair as alt
import pandas as pd
import random

sites = ['Site A', 'Site B', 'Site C', 'Site D']
varieties = ['Variety 1', 'Variety 2', 'Variety 3', 'Variety 4', 'Variety 5']

data_list = []
for site in sites:
    for variety in varieties:
        for _ in range(3):
            data_list.append({'site': site, 'variety': variety, 'yield': random.randint(10, 50)})

source = pd.DataFrame(data_list)

selection = alt.selection_point(fields=['site'], bind='legend')

alt.Chart(source).mark_bar().encode(
    x='sum(yield):Q',
    y='variety:N',
    color='site:N',
    opacity=alt.condition(selection, alt.value(0.9), alt.value(0.2))
).add_params(
    selection
)