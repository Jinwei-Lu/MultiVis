import altair as alt
import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 200
horsepower = np.random.randint(50, 250, size=n_samples)
origin = np.random.choice(['USA', 'Europe', 'Japan'], size=n_samples)
df = pd.DataFrame({'Horsepower': horsepower, 'Origin': origin})

alt.Chart(df).mark_bar().encode(
    alt.X("Horsepower:Q", bin=True),
    alt.Y("count()"),
    alt.Row("Origin:N")
)