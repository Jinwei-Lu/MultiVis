import altair as alt
import pandas as pd
import numpy as np

horsepower = np.random.randint(50, 300, size=150)
cylinders = np.random.choice([4, 6, 8], size=150)
df = pd.DataFrame({'Horsepower': horsepower, 'Cylinders': cylinders.astype(str)})

chart = alt.Chart(df).mark_tick().encode(
    x=alt.X('Horsepower:Q'),
    y=alt.Y('Cylinders:O')
)

chart