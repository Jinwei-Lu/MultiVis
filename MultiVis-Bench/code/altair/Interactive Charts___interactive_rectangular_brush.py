import altair as alt
import pandas as pd
import numpy as np

n_cars = 400
np.random.seed(42)

source = pd.DataFrame({
    'Horsepower': np.random.randint(50, 250, n_cars),
    'Miles_per_Gallon': np.random.randint(10, 50, n_cars) - 0.1 * np.random.randint(50, 250, n_cars),
    'Cylinders': np.random.choice([3, 4, 5, 6, 8], n_cars),
    'Origin': np.random.choice(['USA', 'Europe', 'Japan'], n_cars),
    'Year': np.random.choice(pd.date_range('1970-01-01', '1982-01-01', freq='Y'), size=n_cars),
    'Name': [f'Car {i}' for i in range(n_cars)],
    'Weight_in_lbs': np.random.randint(1500, 5000, n_cars),
    'Acceleration': np.random.randint(8, 25, n_cars),
    'Displacement': np.random.randint(70, 450, n_cars),
})

brush = alt.selection_interval()

alt.Chart(source).mark_point().encode(
    x='Horsepower:Q',
    y='Miles_per_Gallon:Q',
    color=alt.condition(brush, "Cylinders:O", alt.value("grey")),
).add_params(brush)