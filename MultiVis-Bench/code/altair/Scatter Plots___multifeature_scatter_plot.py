import altair as alt
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'sepalLength': np.concatenate([np.random.normal(5.0, 0.3, 50), np.random.normal(6.0, 0.5, 50), np.random.normal(7.0, 0.4, 50)]),
    'sepalWidth': np.concatenate([np.random.normal(3.4, 0.2, 50), np.random.normal(2.7, 0.3, 50), np.random.normal(3.0, 0.2, 50)]),
    'petalWidth': np.concatenate([np.random.normal(0.2, 0.05, 50), np.random.normal(1.3, 0.15, 50), np.random.normal(2.0, 0.2, 50)]),
    'species': ['setosa'] * 50 + ['versicolor'] * 50 + ['virginica'] * 50
})

alt.Chart(data).mark_circle().encode(
    alt.X('sepalLength'),
    alt.Y('sepalWidth'),
    color='species',
    size='petalWidth'
)