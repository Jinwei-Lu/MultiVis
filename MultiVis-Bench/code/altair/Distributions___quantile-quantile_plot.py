import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)
u_data = np.random.normal(0, 1, 1000)
df = pd.DataFrame({'u': u_data})

base = alt.Chart(df).transform_quantile(
    'u',
    step=0.01,
    as_ = ['p', 'v']
).transform_calculate(
    uniform = 'quantileUniform(datum.p)',
    normal = 'quantileNormal(datum.p)'
).mark_point().encode(
    alt.Y('v:Q')
)

chart = base.encode(x='uniform:Q') | base.encode(x='normal:Q')

chart