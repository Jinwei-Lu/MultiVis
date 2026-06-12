import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
data = pd.DataFrame({
    'Horsepower': np.random.randint(50, 250, size=400),
    'Name': [f'Car {i}' for i in range(1, 401)],
    'Origin': np.random.choice(['USA', 'Europe', 'Japan'], size=400),
    'Miles_per_Gallon': np.random.uniform(10, 50, size=400)
})

chart = alt.Chart(data).encode(
    alt.X("bin_Horsepower_start:Q"),
    alt.X2("bin_Horsepower_end:Q"),
    alt.Y("y:O"),
    alt.Y2("y2"),
).transform_bin(
    ["bin_Horsepower_start", "bin_Horsepower_end"],
    field='Horsepower'
).transform_aggregate(
    count='count()',
    groupby=["bin_Horsepower_start", "bin_Horsepower_end"]
).transform_bin(
    ["bin_count_start", "bin_count_end"],
    field='count'
).transform_calculate(
    y="datum.bin_count_end/2",
    y2="-datum.bin_count_end/2",
).transform_joinaggregate(
    max_bin_count_end="max(bin_count_end)",
)

layer1 = chart.mark_bar().encode(
    alt.Color("max_bin_count_end:O")
)
layer2 = chart.mark_bar().encode(
    alt.Color("bin_count_end:O")
)

layer1 + layer2