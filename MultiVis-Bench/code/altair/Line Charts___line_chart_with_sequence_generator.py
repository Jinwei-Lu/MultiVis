import altair as alt
import numpy as np
import pandas as pd

x = np.arange(0, 12.7, 0.1)
sin_y = np.sin(x)
cos_y = np.cos(x)

df = pd.DataFrame({'x': x, 'sin': sin_y, 'cos': cos_y})
df_long = df.melt(id_vars=['x'], value_vars=['sin', 'cos'], var_name='key', value_name='value')

chart = alt.Chart(df_long).mark_line().encode(
    x='x:Q',
    y='value:Q',
    color='key:N'
)

chart