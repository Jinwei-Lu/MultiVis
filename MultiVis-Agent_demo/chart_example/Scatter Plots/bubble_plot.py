import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)

num_points = 100

horsepower = np.random.uniform(50, 300, num_points)
miles_per_gallon = 45 - horsepower / 7 + np.random.normal(0, 5, num_points)
miles_per_gallon = np.clip(miles_per_gallon, 10, 45)
acceleration = np.random.uniform(5, 20, num_points)

data = pd.DataFrame({
    'Horsepower': horsepower,
    'Miles_per_Gallon': miles_per_gallon,
    'Acceleration': acceleration
})

chart = alt.Chart(data).mark_point().encode(
    x='Horsepower:Q',
    y='Miles_per_Gallon:Q',
    size='Acceleration:Q'
)

chart.show()