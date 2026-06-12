import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
n = 100
data = pd.DataFrame({
    'Horsepower': np.random.randint(50, 250, size=n),
    'Miles_per_Gallon':  40 - 0.1 * np.random.randint(50, 250, size=n) + np.random.normal(0, 5, size=n),
    'Origin': np.random.choice(['USA', 'Europe', 'Japan'], size=n),
    'Name': [f'Car_{i}' for i in range(n)],
})

chart = alt.Chart(data).mark_circle().encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
)

chart