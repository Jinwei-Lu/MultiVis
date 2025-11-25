import altair as alt
import pandas as pd
import numpy as np

def generate_car_data(n_samples=392):
    rng = np.random.default_rng(42)
    horsepower = rng.integers(low=40, high=230, size=n_samples)
    mpg = 50 - 0.1 * horsepower + rng.normal(0, 5, size=n_samples)
    mpg = np.clip(mpg, 5, 55)
    acceleration = rng.normal(15, 3, size=n_samples)
    acceleration = np.clip(acceleration, 8, 25)
    origin = rng.choice(["USA", "Europe", "Japan"], size=n_samples, p=[0.6, 0.2, 0.2])
    df = pd.DataFrame({
        'Horsepower': horsepower,
        'Miles_per_Gallon': mpg,
        'Acceleration': acceleration,
        'Origin': origin
    })
    return df

source = generate_car_data()

brush = alt.selection_interval(resolve='global')

base = alt.Chart(source).mark_point().encode(
    y='Miles_per_Gallon',
    color=alt.condition(brush, "Origin:N", alt.value("gray")),
).add_params(
    brush
)

chart = base.encode(x='Horsepower') | base.encode(x='Acceleration')

chart.display()