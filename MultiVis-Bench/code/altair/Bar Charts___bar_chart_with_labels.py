import altair as alt
import pandas as pd
import numpy as np

years = np.arange(1565, 1825, 5)
wheat_values = np.array([41, 45, 42, 49, 41.5, 47, 64, 27, 33, 32, 33, 35, 33, 45, 33, 39, 53, 42, 40.5, 46.5, 32, 37, 43, 35, 27, 40, 50, 30, 32, 44, 33, 29, 39, 26, 32, 27, 27.5, 31, 35.5, 31, 43, 47, 44, 46, 42, 47.5, 76, 79, 81, 99, 78, 54])
wheat_values = wheat_values[:len(years)]

source = pd.DataFrame({'year': years.astype(str), 'wheat': wheat_values})

base = alt.Chart(source).encode(
    x='wheat',
    y="year:O",
    text='wheat'
)

chart = base.mark_bar() + base.mark_text()

chart