import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 150
data = {
    'petalWidth': np.random.normal(1.2, 0.3, n_samples),
    'petalLength': np.random.normal(4.4, 1.0, n_samples),
    'sepalWidth': np.random.normal(3.0, 0.4, n_samples),
    'sepalLength': np.random.normal(5.8, 0.8, n_samples),
}
source = pd.DataFrame(data)

chart = alt.Chart(source).transform_fold(
    ['petalWidth', 'petalLength', 'sepalWidth', 'sepalLength'],
    as_=['Measurement_type', 'value']
).transform_density(
    density='value',
    bandwidth=0.3,
    groupby=['Measurement_type'],
    extent=[0, 8],
    counts=True,
    steps=200
).mark_area().encode(
    alt.X('value:Q'),
    alt.Y('density:Q', stack='zero'),
    alt.Color('Measurement_type:N')
)

chart