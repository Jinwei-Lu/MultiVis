import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 200
data = {
    'Horsepower': np.random.randint(50, 250, size=n_samples),
    'Acceleration': np.random.uniform(8, 25, size=n_samples),
    'Miles_per_Gallon': np.random.uniform(10, 50, size=n_samples),
    'Origin': np.random.choice(['USA', 'Europe', 'Japan'], size=n_samples)
}
df = pd.DataFrame(data)

rows = ['Horsepower', 'Acceleration', 'Miles_per_Gallon']
cols = ['Miles_per_Gallon', 'Acceleration', 'Horsepower']

chart = alt.Chart(df).mark_circle().encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y(alt.repeat("row"), type='quantitative'),
    color='Origin:N'
).repeat(
    row=rows,
    column=cols
)

chart