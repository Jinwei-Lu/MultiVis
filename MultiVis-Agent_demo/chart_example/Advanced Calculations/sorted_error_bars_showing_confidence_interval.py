import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
varieties = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
n_varieties = len(varieties)
n_samples = 20

data = []
for variety in varieties:
    yield_mean = np.random.uniform(20, 40)
    yield_std = np.random.uniform(3, 8)
    yield_values = np.random.normal(yield_mean, yield_std, n_samples)
    for y in yield_values:
        data.append({'variety': variety, 'yield': y})

df = pd.DataFrame(data)

points = alt.Chart(df).mark_point().encode(
    x=alt.X('mean(yield):Q'),
    y=alt.Y('variety:N', sort=alt.EncodingSortField(field='yield', op='mean', order='descending'))
)

error_bars = alt.Chart(df).mark_rule().encode(
    x='ci0(yield):Q',
    x2='ci1(yield):Q',
    y=alt.Y('variety:N', sort=alt.EncodingSortField(field='yield', op='mean', order='descending'))
)

chart = points + error_bars

base = alt.Chart(df).encode(
    y=alt.Y('variety:N', sort=alt.EncodingSortField(field='yield', op='mean', order='descending'))
)

points2 = base.mark_point().encode(
    x=alt.X('mean(yield):Q')
)

error_bars2 = base.mark_rule().encode(
    x='ci0(yield):Q',
    x2='ci1(yield):Q'
)

chart2 = points2 + error_bars2