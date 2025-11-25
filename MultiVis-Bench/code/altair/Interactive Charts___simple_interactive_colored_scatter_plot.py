import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)

n_points = 200
horsepower = np.random.randint(50, 301, n_points)
mpg_base = 40
mpg_decline_rate = 0.1
mpg_noise = np.random.randn(n_points) * 5
miles_per_gallon = mpg_base - horsepower * mpg_decline_rate + mpg_noise
miles_per_gallon = np.clip(miles_per_gallon, 10, 45)
origins = np.random.choice(['USA', 'Europe', 'Japan'], n_points)

source = pd.DataFrame({
    'Horsepower': horsepower,
    'Miles_per_Gallon': miles_per_gallon,
    'Origin': origins
})

alt.Chart(source).mark_circle().encode(
    x='Horsepower:Q',
    y='Miles_per_Gallon:Q',
    color='Origin:N'
)