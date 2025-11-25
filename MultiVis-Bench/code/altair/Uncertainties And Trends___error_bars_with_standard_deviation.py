import altair as alt
import pandas as pd
import numpy as np

varieties = ['Manchuria', 'Glabron', 'No. 475', 'Velvet', 'Trebi', 'Peatland']
mean_yields = [25, 28, 22, 30, 26, 24]
std_devs = [3, 4, 2, 5, 3.5, 2.5]

source = pd.DataFrame({
    'variety': varieties,
    'mean_yield': mean_yields,
    'std_dev': std_devs,
    'lower_yield': np.array(mean_yields) - np.array(std_devs),
    'upper_yield': np.array(mean_yields) + np.array(std_devs)
})

error_bars = alt.Chart(source).mark_errorbar().encode(
    x='lower_yield:Q',
    x2='upper_yield:Q',
    y='variety:N'
)

points = alt.Chart(source).mark_point().encode(
    x='mean_yield:Q',
    y='variety:N'
)

chart = error_bars + points

chart