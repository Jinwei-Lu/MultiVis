import altair as alt
import numpy as np
import pandas as pd

x = np.arange(0, 100)
y = np.sin(x / 5)

source = pd.DataFrame({'x': x, 'f(x)': y})

chart = alt.Chart(source).mark_line().encode(
    x='x',
    y='f(x)'
)

chart