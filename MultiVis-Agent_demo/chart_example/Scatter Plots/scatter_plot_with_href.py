import altair as alt
import pandas as pd
import numpy as np

num_cars = 100
source = pd.DataFrame({
    'Name': [f'Car {i}' for i in range(num_cars)],
    'Horsepower': np.random.randint(50, 200, size=num_cars),
    'Miles_per_Gallon': np.random.randint(15, 50, size=num_cars),
    'Origin': np.random.choice(['USA', 'Europe', 'Japan'], size=num_cars)
})

alt.Chart(source).mark_point().encode(
    x='Horsepower:Q',
    y='Miles_per_Gallon:Q',
    color='Origin:N'
)