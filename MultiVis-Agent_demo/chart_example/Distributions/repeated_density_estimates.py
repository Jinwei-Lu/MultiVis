import altair as alt
import numpy as np
import pandas as pd

np.random.seed(0)
data = {
    'petalWidth': np.random.rand(50) * 2.5,
    'petalLength': np.random.rand(50) * 6 + 1,
    'sepalWidth': np.random.rand(50) * 2 + 2,
    'sepalLength': np.random.rand(50) * 4 + 4,
    'species': ['setosa'] * 50
}
source = pd.DataFrame(data)

df_melted = source.melt(
    value_vars=["petalWidth", "petalLength", "sepalWidth", "sepalLength"],
    var_name="Measurement_type",
    value_name="value",
)

chart = alt.Chart(df_melted).transform_density(
    density='value',
    bandwidth=0.3,
    groupby=['Measurement_type'],
    extent=[0, 8],
    steps=500
).mark_area(
    opacity=0.5,
    interpolate='monotone'
).encode(
    alt.X('value:Q'),
    alt.Y('density:Q', scale=alt.Scale(domainMin=0)),
    alt.Row('Measurement_type:N')
)
chart