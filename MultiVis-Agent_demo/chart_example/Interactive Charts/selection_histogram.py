import altair as alt
import pandas as pd
import numpy as np

def generate_car_data(n_samples=392):
    rng = np.random.default_rng(42)
    horsepower = rng.integers(low=40, high=230, size=n_samples)
    mpg = 35 - 0.1 * horsepower + rng.normal(loc=0, scale=5, size=n_samples)
    mpg = np.clip(mpg, 10, 50)
    origin = rng.choice(['USA', 'Europe', 'Japan'], size=n_samples)
    return pd.DataFrame({'Horsepower': horsepower, 'Miles_per_Gallon': mpg, 'Origin': origin})

source = generate_car_data()

brush = alt.selection_interval()

points = alt.Chart(source).mark_point().encode(
    x='Horsepower:Q',
    y='Miles_per_Gallon:Q',
    color=alt.condition(brush, "Origin:N", alt.value("lightgray"))
).add_params(brush)

bars = alt.Chart(source).mark_bar().encode(
    y='Origin:N',
    x='count(Origin):Q'
).transform_filter(brush)

points & bars