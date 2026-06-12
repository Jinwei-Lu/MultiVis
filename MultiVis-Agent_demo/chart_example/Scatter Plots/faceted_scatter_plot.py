import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 200
data = {
    'Horsepower': np.random.randint(50, 250, size=n_samples),
    'Miles_per_Gallon':  35 - 0.1 * np.random.randint(50, 250, size=n_samples) + np.random.normal(0, 3, size=n_samples),
    'Origin': np.random.choice(['USA', 'Europe', 'Japan'], size=n_samples)
}
df = pd.DataFrame(data)

alt.Chart(df).mark_point().encode(
    x="Horsepower:Q",
    y="Miles_per_Gallon:Q",
    row="Origin:N"
)